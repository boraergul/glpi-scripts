const CLogger = function (serviceName) {
    this.serviceName = serviceName;
    this.INFO = 4;
    this.WARN = 3;
    this.ERROR = 2;
    this.log = function (level, msg) {
        Zabbix.log(level, '[' + this.serviceName + '] ' + msg);
    };
};

const CWebhook = function (value) {
    try {
        params = JSON.parse(value);

        if (['0', '1', '2', '3', '4'].indexOf(params.event_source) === -1) {
            throw 'Incorrect "event_source" parameter given: ' + params.event_source + '.\nMust be 0-4.';
        }

        this.runCallback = function (name, params) {
            if (typeof this[name] === 'function') {
                return this[name].apply(this, [params]);
            }
        };

        this.handleEvent = function (source, event) {
            const alert = { source: source, event: event };
            return [
                this.runCallback('on' + source + event, alert),
                this.runCallback('on' + event, alert),
                this.runCallback('onEvent', alert)
            ];
        };

        this.run = function () {
            var results = [];
            const types = { '0': 'Trigger', '1': 'Discovery', '2': 'Autoreg', '3': 'Internal', '4': 'Service' };

            if (['0', '3', '4'].indexOf(this.params.event_source) !== -1) {
                var event = (this.params.event_update_status === '1')
                    ? 'Update'
                    : ((this.params.event_value === '1') ? 'Problem' : 'Resolve');

                results = this.handleEvent(types[this.params.event_source], event);
            }

            for (var idx in results) {
                if (typeof results[idx] !== 'undefined') {
                    return JSON.stringify(results[idx]);
                }
            }

            return JSON.stringify({ status: 'ok', message: 'İşlem tamamlandı fakat ek veri üretilmedi.' });
        };

        this.params = params;
        this.runCallback('onCheckParams', {});
    } catch (error) {
        throw 'Webhook processing failed: ' + error;
    }
};

const CParamValidator = {
    isDefined: function (value) { return typeof value !== 'undefined'; },
    isEmpty: function (value) { return (value.trim() === ''); },
    checkURL: function (value) {
        if (typeof value !== 'string' || !value.match(/^(http|https):\/\/.+/)) { throw 'URL must contain a schema.'; }
        return value.endsWith('/') ? value.slice(0, -1) : value;
    },
    validate: function (rules, params) {
        for (var key in rules) {
            if (rules[key].url) params[key] = this.checkURL(params[key]);
        }
    },
    isMacroSet: function (value) {
        return (typeof value === 'string' && value.length > 0 && !(value.startsWith('{') && value.endsWith('}')));
    }
};

const CHttpRequest = function (logger) {
    this.logger = logger;

    // Her istek için yeni HttpRequest oluştur
    this.createRequest = function () {
        return new HttpRequest();
    };

    this.jsonRequest = function (method, url, data, headers) {
        var isGet = method.toLowerCase() === 'get';
        var finalUrl = url;

        // GET isteğinde data varsa query string yap
        if (isGet && data) {
            var queryString = [];

            var buildQuery = function (obj, prefix) {
                for (var p in obj) {
                    if (obj.hasOwnProperty(p)) {
                        var k = prefix ? prefix + "[" + p + "]" : p;
                        var v = obj[p];
                        if (typeof v === "object" && v !== null) {
                            buildQuery(v, k);
                        } else {
                            queryString.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
                        }
                    }
                }
            };

            buildQuery(data);

            if (queryString.length > 0) {
                finalUrl += (url.indexOf('?') === -1 ? '?' : '&') + queryString.join('&');
            }
        }

        // Her istek için temiz HttpRequest objesi oluştur
        var req = this.createRequest();

        // Header'ları ekle
        if (headers) {
            for (var key in headers) {
                req.addHeader(key + ': ' + headers[key]);
            }
        }

        // POST/PUT için Content-Type ekle
        if (!isGet) {
            req.addHeader('Content-Type: application/json');
        }

        // İsteği yap
        var resp;
        if (isGet) {
            resp = req.get(finalUrl);
        } else {
            var body = data ? JSON.stringify(data) : null;
            resp = req[method.toLowerCase()](finalUrl, body);
        }

        this.logger.log(3, 'API Call - Method: ' + method + ' URL: ' + finalUrl);
        this.logger.log(3, 'API Response: ' + resp);

        try {
            return JSON.parse(resp);
        } catch (e) {
            this.logger.log(2, 'JSON Parse Error: ' + e);
            throw 'Invalid JSON response: ' + resp;
        }
    };
};

const serviceLogName = 'GLPi Webhook v2',
    Logger = new CLogger(serviceLogName);

CWebhook.prototype.onCheckParams = function () {
    CParamValidator.validate({
        zabbix_url: { url: true },
        glpi_url: { url: true }
    }, this.params);
};

CWebhook.prototype.getAuthToken = function () {
    var headers = {
        'Authorization': 'user_token ' + this.params.glpi_user_token,
        'App-Token': this.params.glpi_app_token
    };

    var resp = this.request.jsonRequest('post', this.params.glpi_url + '/apirest.php/initSession', {}, headers);
    if (!resp.session_token) { throw 'Auth failed: Session token not found'; }
    Logger.log(3, 'Session token obtained successfully');
    return resp.session_token;
};

CWebhook.prototype.findAsset = function (hostname) {
    if (!hostname) {
        Logger.log(3, 'Asset search skipped: Hostname is empty.');
        return null;
    }

    Logger.log(3, '=== ASSET SEARCH START ===');
    Logger.log(3, 'Searching for hostname: "' + hostname + '"');

    var headers = {
        'Session-Token': this.params.authToken,
        'App-Token': this.params.glpi_app_token
    };

    // Helper to get Asset Details
    var getAssetDetails = function (webhook, type, id) {
        try {
            var detailResp = webhook.request.jsonRequest('get', webhook.params.glpi_url + '/apirest.php/' + type + '/' + id, null, headers);
            Logger.log(3, type + ' ' + id + ' entities_id: ' + detailResp.entities_id);
            return detailResp.entities_id || 0;
        } catch (e) {
            Logger.log(3, 'Failed to get details for ' + type + ' ' + id + ': ' + e);
            return 0;
        }
    };

    var searchParams = {
        'criteria[0][field]': 1,
        'criteria[0][searchtype]': 'contains',
        'criteria[0][value]': hostname,
        'forcedisplay[0]': 2,
        'expand_dropdowns': 'false'
    };

    // 1. Bilgisayar (Computer) Ara
    try {
        Logger.log(3, 'Searching Computer...');

        var respComp = this.request.jsonRequest('get', this.params.glpi_url + '/apirest.php/search/Computer', searchParams, headers);
        Logger.log(3, 'Computer search result - totalcount: ' + respComp.totalcount);

        if (respComp.totalcount > 0 && respComp.data && respComp.data.length > 0) {
            var item = respComp.data[0];
            var id = item['2'];
            var entId = getAssetDetails(this, 'Computer', id);

            Logger.log(3, '>>> FOUND Computer: hostname=' + hostname + ' id=' + id + ' entity_id=' + entId);
            Logger.log(3, '=== ASSET SEARCH END (SUCCESS) ===');
            return { id: id, type: 'Computer', entities_id: entId };
        } else {
            Logger.log(3, 'No Computer found');
        }
    } catch (e) {
        Logger.log(3, 'Computer search error: ' + e);
    }

    // 2. Ağ Cihazı (NetworkEquipment) Ara
    try {
        Logger.log(3, 'Searching NetworkEquipment...');

        var respNet = this.request.jsonRequest('get', this.params.glpi_url + '/apirest.php/search/NetworkEquipment', searchParams, headers);
        Logger.log(3, 'NetworkEquipment search result - totalcount: ' + respNet.totalcount);

        if (respNet.totalcount > 0 && respNet.data && respNet.data.length > 0) {
            var item = respNet.data[0];
            var id = item['2'];
            var entId = getAssetDetails(this, 'NetworkEquipment', id);

            Logger.log(3, '>>> FOUND NetworkEquipment: hostname=' + hostname + ' id=' + id + ' entity_id=' + entId);
            Logger.log(3, '=== ASSET SEARCH END (SUCCESS) ===');
            return { id: id, type: 'NetworkEquipment', entities_id: entId };
        } else {
            Logger.log(3, 'No NetworkEquipment found');
        }
    } catch (e) {
        Logger.log(3, 'NetworkEquipment search error: ' + e);
    }

    Logger.log(3, 'Asset NOT found for hostname: "' + hostname + '". Using Default Entity (0).');
    Logger.log(3, '=== ASSET SEARCH END (NOT FOUND) ===');
    return null;
};

const REQUEST_SOURCE_ID = 8; // "Monitoring" seçeneğinin ID'si

CWebhook.prototype.createTicket = function () {
    Logger.log(3, '>>> CREATE TICKET START <<<');
    Logger.log(3, 'Host: "' + this.params.host + '"');

    // Varlık Ara
    var asset = this.findAsset(this.params.host);
    var entityId = asset ? asset.entities_id : 0;

    Logger.log(3, '>>> Asset result: ' + JSON.stringify(asset));
    Logger.log(3, '>>> Entity ID to use: ' + entityId);

    // Severity Mapping
    var urgency = 3, impact = 3, priority = 3;
    var sevMap = {
        'Disaster': [5, 5, 5],
        'High': [4, 4, 4],
        'Average': [3, 3, 3],
        'Warning': [3, 2, 2],
        'Information': [2, 1, 1]
    };

    if (sevMap[this.params.event_severity]) {
        urgency = sevMap[this.params.event_severity][0];
        impact = sevMap[this.params.event_severity][1];
        priority = sevMap[this.params.event_severity][2];
    }

    var ticketData = {
        input: {
            name: this.params.alert_subject,
            content: this.params.alert_message + '\n\n<a href="' + this.params.zabbix_url + '">Zabbix Link</a>',
            urgency: urgency,
            impact: impact,
            priority: priority,
            type: 1,
            itilcategories_id: 228,
            requesttypes_id: REQUEST_SOURCE_ID,
            '_groups_id_assign': 7,
            entities_id: entityId
        }
    };

    if (asset) {
        ticketData.input.items_id = {};
        ticketData.input.items_id[asset.type] = [asset.id];
        Logger.log(3, '>>> Linking asset: ' + asset.type + ' ID=' + asset.id);
    }

    var headers = {
        'Session-Token': this.params.authToken,
        'App-Token': this.params.glpi_app_token
    };

    Logger.log(3, '>>> Creating ticket with data: ' + JSON.stringify(ticketData));
    var resp = this.request.jsonRequest('post', this.params.glpi_url + '/apirest.php/Ticket/', ticketData, headers);
    Logger.log(3, '>>> Ticket created with ID: ' + resp.id);
    Logger.log(3, '>>> CREATE TICKET END <<<');

    return resp.id;
};

CWebhook.prototype.updateTicket = function (status) {
    Logger.log(3, '>>> UPDATE TICKET START <<<');
    Logger.log(3, 'Updating ticket ' + this.params.glpi_ticket_id + ' to status: ' + status);

    var headers = {
        'Session-Token': this.params.authToken,
        'App-Token': this.params.glpi_app_token
    };

    // SOLVED (5) için önce Followup ekle
    if (status === 5) {
        try {
            var followupData = {
                input: {
                    itemtype: 'Ticket',
                    items_id: this.params.glpi_ticket_id,
                    content: '<b>Zabbix Recovery:</b><br>' + this.params.alert_message + '<br><a href="' + this.params.zabbix_url + '">Zabbix Link</a>'
                }
            };
            var folResp = this.request.jsonRequest('post', this.params.glpi_url + '/apirest.php/ITILFollowup', followupData, headers);
            Logger.log(3, 'Followup added successfully');
        } catch (e) {
            Logger.log(3, 'Failed to add recovery followup (Non-critical): ' + e);
        }
    }

    // Status Güncelle
    try {
        var updateData = { input: { id: this.params.glpi_ticket_id, status: status } };
        var upResp = this.request.jsonRequest('put', this.params.glpi_url + '/apirest.php/Ticket/' + this.params.glpi_ticket_id, updateData, headers);
        Logger.log(3, 'Status updated successfully');
        Logger.log(3, '>>> UPDATE TICKET END <<<');
        return upResp;
    } catch (e) {
        Logger.log(2, 'Failed to update ticket status (Critical): ' + e);
        throw e;
    }
};

CWebhook.prototype.onProblem = function () {
    Logger.log(3, '>>> onProblem triggered <<<');
    const id = this.createTicket();
    return {
        tags: {
            '__zbx_glpi_ticket_id': id,
            '__zbx_glpi_link': this.params.glpi_url + '/front/ticket.form.php?id=' + id
        }
    };
};

CWebhook.prototype.onResolve = function () {
    Logger.log(3, '>>> onResolve triggered <<<');
    Logger.log(3, 'Ticket ID: ' + this.params.glpi_ticket_id);
    if (!this.params.glpi_ticket_id || this.params.glpi_ticket_id.startsWith('{')) {
        Logger.log(3, 'CRITICAL: glpi_ticket_id is missing or macro not resolved!');
    }
    this.updateTicket(5); // 5 = Solved
    return { status: 'resolved', ticket_id: this.params.glpi_ticket_id, tags: {} };
};

CWebhook.prototype.onUpdate = function () {
    Logger.log(3, '>>> onUpdate triggered <<<');
    this.updateTicket(2); // 2 = Processing
    return { status: 'updated', ticket_id: this.params.glpi_ticket_id, tags: {} };
};

try {
    var hook = new CWebhook(value);
    hook.request = new CHttpRequest(Logger);
    hook.params.authToken = hook.getAuthToken();
    return hook.run();
} catch (error) {
    Logger.log(2, 'Webhook failed: ' + error);
    throw 'Sending failed: ' + error;
}