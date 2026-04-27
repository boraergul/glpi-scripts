<?php

class PluginSlareportReport extends CommonGLPI
{
    private static $translations = null;

    /**
     * Custom translation helper to bypass GLPI locale issues
     */
    static function trans($key)
    {
        if (self::$translations === null) {
            $current_lang = $_SESSION['glpilanguage'] ?? 'en_GB';
            $loc_file = GLPI_ROOT . "/plugins/slareport/locales/" . $current_lang . ".php";
            if (!file_exists($loc_file)) {
                $loc_file = GLPI_ROOT . "/plugins/slareport/locales/en_GB.php";
            }
            if (file_exists($loc_file)) {
                self::$translations = include($loc_file);
            } else {
                self::$translations = [];
            }
        }
        return self::$translations[$key] ?? $key;
    }

    static function getTypeName($nb = 0)
    {
        return self::trans('SLA_Report_Title');
    }

    static function getMenuName()
    {
        return self::trans('SLA_Report_Title');
    }

    static function getMenuContent()
    {
        return [
            'title' => self::trans('SLA_Report_Title'),
            'page' => "/plugins/slareport/front/index.php",
            'icon' => 'fas fa-chart-pie'
        ];
    }

    /**
     * Get all entities for filtering
     */
    static function getEntities()
    {
        global $DB;
        $entities = [];
        $iterator = $DB->request(['FROM' => 'glpi_entities', 'ORDER' => 'completename']);
        foreach ($iterator as $data) {
            $name_parts = explode(' > ', $data['completename']);
            $entities[$data['id']] = end($name_parts);
        }
        return $entities;
    }

    /**
     * Get SLA definitions
     */
    static function getSlaDefinitions()
    {
        global $DB;
        $slas = [];
        $iterator = $DB->request(['FROM' => 'glpi_slas']);
        foreach ($iterator as $data) {
            $slas[$data['id']] = $data;
        }
        return $slas;
    }

    /**
     * Main data calculation method
     */
    static function getSlaComplianceData($start_date, $end_date, $entity_id = 0, $sort = 'glpi_tickets.id', $order = 'DESC')
    {
        global $DB;

        // Security: Allow-list for sorting
        $allowed_sorts = [
            'glpi_tickets.id',
            'glpi_tickets.name',
            'glpi_entities.completename',
            'glpi_tickets.date'
        ];
        if (!in_array($sort, $allowed_sorts)) {
            $sort = 'glpi_tickets.id';
        }

        $allowed_orders = ['ASC', 'DESC'];
        if (!in_array(strtoupper($order), $allowed_orders)) {
            $order = 'DESC';
        }

        $slas = self::getSlaDefinitions();
        $entities = self::getEntities();

        $where = [
            'glpi_tickets.is_deleted' => 0,
            ['glpi_tickets.date' => ['>=', $start_date . ' 00:00:00']],
            ['glpi_tickets.date' => ['<=', $end_date . ' 23:59:59']]
        ];

        if ($entity_id > 0) {
            $where['glpi_tickets.entities_id'] = getSonsOf('glpi_entities', $entity_id);
        }

        $iterator = $DB->request([
            'SELECT' => [
                'glpi_tickets.id',
                'glpi_tickets.name',
                'glpi_tickets.date',
                'glpi_tickets.solvedate',
                'glpi_tickets.entities_id',
                'glpi_tickets.slas_id_ttr',
                'glpi_tickets.slas_id_tto',
                'glpi_tickets.status',
                'glpi_tickets.time_to_resolve',
                'glpi_tickets.time_to_own',
                'glpi_tickets.solve_delay_stat',
                'glpi_tickets.takeintoaccount_delay_stat',
                'glpi_entities.completename AS entity_completename',
                'glpi_pendingreasons.name AS pending_reason'
            ],
            'FROM'   => 'glpi_tickets',
            'LEFT JOIN' => [
                'glpi_entities' => [
                    'ON' => [
                        'glpi_tickets' => 'entities_id',
                        'glpi_entities' => 'id'
                    ]
                ],
                'glpi_pendingreasons_items' => [
                    'ON' => [
                        'glpi_pendingreasons_items' => 'items_id',
                        'glpi_tickets'              => 'id'
                    ]
                ],
                'glpi_pendingreasons' => [
                    'ON' => [
                        'glpi_pendingreasons_items' => 'pendingreasons_id',
                        'glpi_pendingreasons' => 'id'
                    ]
                ]
            ],
            'WHERE'  => $where,
            'ORDER'  => $sort . " " . $order
        ]);

        $summary = [
            'total_tickets' => 0,
            'sla_total' => 0,
            'sla_ok' => 0,
            'sla_violated' => 0,
            'sla_tto_violated' => 0,
            'sla_ttr_violated' => 0,
            'sla_active' => 0,
            'sla_waiting' => 0,
            'sla_none' => 0,
            'entities' => []
        ];

        $tickets = [];
        $current_time = date('Y-m-d H:i:s');

        $ticket_ids = [];
        $ticket_records = [];
        foreach ($iterator as $ticket) {
            $ticket_ids[] = (int)$ticket['id'];
            $ticket_records[] = $ticket;
        }

        $pending_stats = self::calculatePendingStats($ticket_ids);

        foreach ($ticket_records as $ticket) {
            $tid = (int)$ticket['id'];
            $summary['total_tickets']++;

            $entity_id_ticket = (int) $ticket['entities_id'];
            $entity_name = (isset($entities[$entity_id_ticket]) ? $entities[$entity_id_ticket] : 'Unknown');

            if (!isset($summary['entities'][$entity_name])) {
                $summary['entities'][$entity_name] = [
                    'total' => 0,
                    'sla_total' => 0,
                    'sla_ok' => 0,
                    'sla_violated' => 0,
                    'sla_tto_violated' => 0,
                    'sla_ttr_violated' => 0,
                    'sla_active' => 0,
                    'sla_waiting' => 0,
                    'sla_none' => 0
                ];
            }
            $summary['entities'][$entity_name]['total']++;

            $sla_ttr_id = (int) $ticket['slas_id_ttr'];
            $sla_tto_id = (int) $ticket['slas_id_tto'];

            if ($sla_ttr_id == 0 && $sla_tto_id == 0) {
                $summary['sla_none']++;
                $summary['entities'][$entity_name]['sla_none']++;
                $status = 'none';
                $status_label = self::trans('SLA_Not_Defined');
                $violation_type = '';
            } else {
                $summary['sla_total']++;
                $summary['entities'][$entity_name]['sla_total']++;

                $status = 'compliant';
                $violation_type = '';

                // TTR Calculation
                $ttr_violated = false;
                if ($sla_ttr_id > 0) {
                    if (in_array($ticket['status'], [CommonITILObject::SOLVED, CommonITILObject::CLOSED])) {
                        if (!empty($ticket['time_to_resolve']) && $ticket['solvedate'] > $ticket['time_to_resolve']) {
                            $ttr_violated = true;
                        }
                    } elseif (!empty($ticket['time_to_resolve'])) {
                        if ($current_time > $ticket['time_to_resolve']) {
                            $ttr_violated = true;
                        } else {
                            $status = 'active';
                        }
                    }
                }

                // TTO Calculation
                $tto_violated = false;
                if ($sla_tto_id > 0) {
                    if ($ticket['status'] == CommonITILObject::INCOMING) {
                        if (!empty($ticket['time_to_own']) && $current_time > $ticket['time_to_own']) {
                            $tto_violated = true;
                        } elseif (!empty($ticket['time_to_own'])) {
                            $status = 'active';
                        }
                    } else {
                        if (isset($slas[$sla_tto_id])) {
                            $sla = $slas[$sla_tto_id];
                            $limit = self::convertToSeconds($sla['number_time'], $sla['definition_time']);
                            $tto_delay = (int) $ticket['takeintoaccount_delay_stat'];
                            if ($tto_delay > 0 && $tto_delay > $limit) {
                                $tto_violated = true;
                            }
                        }
                    }
                }

                if ($tto_violated || $ttr_violated) {
                    $status = 'violated';
                    if ($tto_violated && $ttr_violated) {
                        $violation_type = 'TTO + TTR';
                        $summary['sla_tto_violated']++;
                        $summary['sla_ttr_violated']++;
                    } elseif ($tto_violated) {
                        $violation_type = 'TTO';
                        $summary['sla_tto_violated']++;
                    } else {
                        $violation_type = 'TTR';
                        $summary['sla_ttr_violated']++;
                    }
                }

                if ($ticket['status'] == CommonITILObject::WAITING) {
                    $status = 'waiting';
                }

                $status_key = ($status == 'violated' ? 'violated' : ($status == 'active' ? 'active' : ($status == 'waiting' ? 'waiting' : 'ok')));
                $summary['sla_' . $status_key]++;
                $summary['entities'][$entity_name]['sla_' . $status_key]++;

                $status_label = ($status == 'violated' ? self::trans('SLA_Violated_Label') : ($status == 'active' ? self::trans('SLA_Active_Label') : ($status == 'waiting' ? self::trans('SLA_Pending_Label') : self::trans('SLA_Compliant_Label'))));
            }

            $tickets[] = [
                'id' => $ticket['id'],
                'name' => $ticket['name'],
                'date' => $ticket['date'],
                'solvedate' => $ticket['solvedate'],
                'entity' => $entity_name,
                'status' => $status,
                'status_label' => $status_label,
                'violation_type' => $violation_type,
                'ttr_deadline' => $ticket['time_to_resolve'],
                'tto_deadline' => $ticket['time_to_own'],
                'solve_delay_stat' => $ticket['solve_delay_stat'],
                'tto_delay_stat' => $ticket['takeintoaccount_delay_stat'],
                'solve_delay_formatted' => self::formatInterval($ticket['solve_delay_stat']),
                'tto_delay_formatted' => self::formatInterval($ticket['takeintoaccount_delay_stat']),
                'sla_name' => implode(' / ', array_filter([
                    isset($slas[$ticket['slas_id_ttr']]) ? $slas[$ticket['slas_id_ttr']]['name'] : null,
                    isset($slas[$ticket['slas_id_tto']]) ? $slas[$ticket['slas_id_tto']]['name'] : null
                ])),
                'pending_seconds' => $pending_stats[$tid]['total_time'] ?? 0,
                'pending_formatted' => self::formatInterval($pending_stats[$tid]['total_time'] ?? 0),
                'pending_reason' => $ticket['pending_reason'] ?: '',
                'pending_ratio' => 0,
                'breach_probability' => 0,
                'audit' => [
                    'risk_level' => 'normal',
                    'flags'      => []
                ]
            ];

            $ttr_seconds = 0;
            if ($sla_ttr_id > 0 && isset($slas[$sla_ttr_id])) {
                $sla_ttr = $slas[$sla_ttr_id];
                $ttr_seconds = self::convertToSeconds($sla_ttr['number_time'], $sla_ttr['definition_time']);
            }

            if ($ttr_seconds > 0) {
                $p_seconds = $pending_stats[$tid]['total_time'] ?? 0;
                $ratio = $p_seconds / $ttr_seconds;
                $prob = min(100, round($ratio * 100, 1));

                $idx = count($tickets) - 1;
                $tickets[$idx]['pending_ratio'] = $ratio;
                $tickets[$idx]['breach_probability'] = $prob;

                $flags = [];
                $risk_score = 0;

                if ($ratio > 1.0) {
                    $flags[] = 'stagnant';
                    $risk_score += 2;
                } elseif ($ratio > 0.7) {
                    $flags[] = 'high_pending';
                    $risk_score += 1;
                }

                if ($pending_stats[$tid]['first_pending_start']) {
                    $ttr_limit_date = $ticket['time_to_resolve'];
                    $opening_date = $ticket['date'];
                    if ($ttr_limit_date && $opening_date) {
                        $total_sla_time = strtotime($ttr_limit_date) - strtotime($opening_date);
                        $elapsed_at_pending = strtotime($pending_stats[$tid]['first_pending_start']) - strtotime($opening_date);
                        if ($total_sla_time > 0 && ($elapsed_at_pending / $total_sla_time) > 0.9) {
                            $flags[] = 'last_minute';
                            $risk_score += 3;
                        }
                    }
                }

                if ($pending_stats[$tid]['toggles'] > 3) {
                    $flags[] = 'excessive_toggling';
                    $risk_score += 2;
                }

                $tickets[$idx]['audit']['flags'] = $flags;
                $tickets[$idx]['audit']['risk_level'] = ($risk_score >= 3 ? 'high' : ($risk_score >= 1 ? 'suspicious' : 'normal'));
            }
        }

        return [
            'summary' => $summary,
            'tickets' => $tickets
        ];
    }

    static function calculatePendingStats(array $ticket_ids)
    {
        global $DB;
        if (empty($ticket_ids)) {
            return [];
        }

        $pending_data = [];
        foreach ($ticket_ids as $id) {
            $pending_data[$id] = [
                'total_time' => 0,
                'toggles' => 0,
                'first_pending_start' => null,
                'last_start' => null
            ];
        }
        
        $logs = $DB->request([
            'SELECT' => ['id', 'items_id', 'date_mod', 'new_value', 'old_value'],
            'FROM'   => 'glpi_logs',
            'WHERE'  => [
                'itemtype'         => 'Ticket',
                'items_id'         => $ticket_ids,
                'id_search_option' => 12 
            ],
            'ORDER'  => 'date_mod ASC'
        ]);

        foreach ($logs as $log) {
            $tid = $log['items_id'];
            if ($log['new_value'] == CommonITILObject::WAITING) {
                $pending_data[$tid]['toggles']++;
                $pending_data[$tid]['last_start'] = $log['date_mod'];
                if (!$pending_data[$tid]['first_pending_start']) {
                    $pending_data[$tid]['first_pending_start'] = $log['date_mod'];
                }
            } elseif ($log['old_value'] == CommonITILObject::WAITING && $pending_data[$tid]['last_start']) {
                $start = strtotime($pending_data[$tid]['last_start']);
                $end = strtotime($log['date_mod']);
                if ($end > $start) {
                    $pending_data[$tid]['total_time'] += ($end - $start);
                }
                $pending_data[$tid]['last_start'] = null;
            }
        }

        $current_tickets = $DB->request([
            'SELECT' => ['id', 'status'],
            'FROM'   => 'glpi_tickets',
            'WHERE'  => [
                'id'     => $ticket_ids,
                'status' => CommonITILObject::WAITING
            ]
        ]);
        
        $now = time();
        foreach ($current_tickets as $ticket) {
            $tid = $ticket['id'];
            if (isset($pending_data[$tid]) && $pending_data[$tid]['last_start']) {
                $start = strtotime($pending_data[$tid]['last_start']);
                if ($now > $start) {
                    $pending_data[$tid]['total_time'] += ($now - $start);
                }
            }
        }

        return $pending_data;
    }

    static function convertToSeconds($number, $definition)
    {
        switch ($definition) {
            case 'minute': return $number * 60;
            case 'hour': return $number * 3600;
            case 'day': return $number * 86400;
            default: return $number * 3600;
        }
    }

    static function formatInterval($seconds)
    {
        if ($seconds <= 0) return "-";
        $h = floor($seconds / 3600);
        $m = floor(($seconds % 3600) / 60);
        if ($h > 0) {
            return sprintf(self::trans('SLA_Time_HM'), $h, $m);
        }
        return sprintf(self::trans('SLA_Time_M'), $m);
    }
}
