const CLogger = function(serviceName) {
    this.serviceName = serviceName;
    this.INFO = 4;
    this.WARN = 3;
    this.ERROR = 2;
    this.log = function(level, msg) {
        Zabbix.log(level, '[' + this.serviceName + '] ' + msg);
    };
};

const CWebhook = function(value) {
    try {
        params = JSON.parse(value);

        if (['0', '1', '2', '3', '4'].indexOf(params.event_source) === -1) {
            throw 'Incorrect "event_source" parameter given: ' + params.event_source + '.\nMust be 0-4.';
        }

        this.runCallback = function(name, params) {
            if (typeof this[name] === 'function') {
                return this[name].apply(this, [params]);
            }
        };

        this.handleEvent = function(source, event) {
            const alert = { source: source, event: event };
            return [
                this.runCallback('on' + source + event, alert),
                this.runCallback('on' + event, alert),
                this.runCallback('onEvent', alert)
            ];
        };

        this.run = function() {
            var results = [];
            const types = { '0': 'Trigger', '1': 'Discovery', '2': 'Autoreg', '3': 'Internal', '4': 'Service' };

            if (['0', '3', '4'].indexOf(this.params.event_source) !== -1) {
                var event = (this.params.event_update_status === '1')
                    ? 'Update'
                    : ((this.params.event_value === '1') ? 'Problem' : 'Resolve');

                results = this.handleEvent(types[this.params.event_source], event);
            }

            // Undefined hatasını önleyen kritik döngü
            for (var idx in results) {
                if (typeof results[idx] !== 'undefined') {
                    return JSON.stringify(results[idx]);
                }
            }
            
            // Eğer hiçbir fonksiyon değer dönmezse varsayılan başarı mesajı
            return JSON.stringify({ status: 'ok', message: 'İşlem tamamlandı fakat ek veri üretilmedi.' });
        };

        this.params = params;
        this.runCallback('onCheckParams', {});
    } catch (error) {
        throw 'Webhook processing failed: ' + error;
    }
};

const CParamValidator = {
    isDefined: function(value) { return typeof value !== 'undefined'; },
    isEmpty: function(value) { return (value.trim() === ''); },
    checkURL: function(value) {
        if (typeof value !== 'string' || !value.match(/^(http|https):\/\/.+/)) { throw 'URL must contain a schema.'; }
        return value.endsWith('/') ? value.slice(0, -1) : value;
    },
    validate: function(rules, params) {
        for (var key in rules) {
            if (rules[key].url) params[key] = this.checkURL(params[key]);
        }
    },
    isMacroSet: function(value) {
        return (typeof value === 'string' && value.length > 0 && !(value.startsWith('{') && value.endsWith('}')));
    }
};

const CHttpRequest = function(logger) {
    this.request = new HttpRequest();
    this.logger = logger;
    this.addHeaders = function(headers) {
        for (var key in headers) { this.request.addHeader(key + ': ' + headers[key]); }
    };
    this.jsonRequest = function(method, url, data) {
        this.request.addHeader('Content-Type: application/json');
        var resp = this.request[method.toLowerCase()](url, JSON.stringify(data));
        this.logger.log(4, 'Method: ' + method + ' URL: ' + url + ' Response: ' + resp);
        return JSON.parse(resp);
    };
    this.getStatus = function() { return this.request.getStatus(); };
};

const serviceLogName = 'GLPi Webhook',
    Logger = new CLogger(serviceLogName);

CWebhook.prototype.onCheckParams = function () {
    CParamValidator.validate({
        zabbix_url: { url: true },
        glpi_url: { url: true }
    }, this.params);

    if (this.params.event_value !== '1' && CParamValidator.isMacroSet(this.params.glpi_ticket_id)) {
        this.params.event_update_status = '1';
    }

    this.data = {
        input: {
            name: this.params.alert_subject,
            content: this.params.alert_message + '<br><a href="' + this.params.zabbix_url + '">Zabbix Link</a>',
            urgency: 3
        }
    };
};

CWebhook.prototype.getAuthToken = function () {
    var headers = { 'Authorization': 'user_token ' + this.params.glpi_user_token };
    if (this.params.glpi_app_token) headers['App-Token'] = this.params.glpi_app_token;
    
    this.request.addHeaders(headers);
    var resp = this.request.jsonRequest('post', this.params.glpi_url + '/apirest.php/initSession', {});
    if (!resp.session_token) { throw 'Auth failed: Session token not found'; }
    return resp.session_token;
};

CWebhook.prototype.createTicket = function () {
    this.request.request.clearHeader();
    this.request.addHeaders({ 'Session-Token': this.params.authToken, 'App-Token': this.params.glpi_app_token });
    var resp = this.request.jsonRequest('post', this.params.glpi_url + '/apirest.php/Ticket/', this.data);
    return resp.id;
};

CWebhook.prototype.updateTicket = function (status) {
    this.request.request.clearHeader();
    this.request.addHeaders({ 'Session-Token': this.params.authToken, 'App-Token': this.params.glpi_app_token });
    
    var updateData = { input: { id: this.params.glpi_ticket_id, status: status } };
    this.request.jsonRequest('put', this.params.glpi_url + '/apirest.php/Ticket/' + this.params.glpi_ticket_id, updateData);
    
    var followupData = {
        input: {
            itemtype: 'Ticket',
            items_id: this.params.glpi_ticket_id,
            content: this.params.alert_message + '<br><a href="' + this.params.zabbix_url + '">Zabbix Link</a>'
        }
    };
    return this.request.jsonRequest('post', this.params.glpi_url + '/apirest.php/ITILFollowup', followupData);
};

CWebhook.prototype.onProblem = function () {
    const id = this.createTicket();
    return {
        tags: {
            '__zbx_glpi_ticket_id': id,
            '__zbx_glpi_link': this.params.glpi_url + '/front/ticket.form.php?id=' + id
        }
    };
};

CWebhook.prototype.onResolve = function () {
    this.updateTicket(5); // 5 = Solved
    return { status: 'resolved', ticket_id: this.params.glpi_ticket_id };
};

CWebhook.prototype.onUpdate = function () {
    this.updateTicket(2); // 2 = Processing (İsteğe bağlı)
    return { status: 'updated', ticket_id: this.params.glpi_ticket_id };
};

try {
    var hook = new CWebhook(value);
    hook.request = new CHttpRequest(Logger);
    hook.params.authToken = hook.getAuthToken();
    return hook.run();
} catch (error) {
    throw 'Sending failed: ' + error;
}