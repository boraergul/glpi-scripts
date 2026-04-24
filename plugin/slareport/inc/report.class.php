<?php

class PluginSlareportReport extends CommonGLPI
{
    static function getTypeName($nb = 0)
    {
        return __('SLA Breach Report', 'slareport');
    }

    static function getMenuName()
    {
        return __('SLA Breach Report', 'slareport');
    }

    static function getMenuContent()
    {
        return [
            'title' => __('SLA Breach Report', 'slareport'),
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
    static function getSlaComplianceData($start_date, $end_date, $entity_id = 0, $sort = 'glpi_tickets.date', $order = 'DESC')
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
            $sort = 'glpi_tickets.date';
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
                'glpi_entities.completename AS entity_completename'
            ],
            'FROM'   => 'glpi_tickets',
            'LEFT JOIN' => [
                'glpi_entities' => [
                    'ON' => [
                        'glpi_tickets' => 'entities_id',
                        'glpi_entities' => 'id'
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
            'sla_none' => 0,
            'entities' => []
        ];

        $tickets = [];
        $current_time = date('Y-m-d H:i:s');

        // Collect ticket IDs for batch pending time calculation
        $ticket_ids = [];
        $ticket_records = [];
        foreach ($iterator as $ticket) {
            $ticket_ids[] = (int)$ticket['id'];
            $ticket_records[] = $ticket;
        }

        $pending_times = self::calculateTotalPendingTime($ticket_ids);

        foreach ($ticket_records as $ticket) {
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
                    'sla_none' => 0
                ];
            }
            $summary['entities'][$entity_name]['total']++;

            $sla_ttr_id = (int) $ticket['slas_id_ttr'];
            $sla_tto_id = (int) $ticket['slas_id_tto'];

            if ($sla_ttr_id == 0 && $sla_tto_id == 0) {
                // Non-SLA Ticket
                $summary['sla_none']++;
                $summary['entities'][$entity_name]['sla_none']++;
                $status = 'none';
                $status_label = __('SLA Not Defined', 'slareport');
                $violation_type = '';
            } else {
                // SLA Ticket
                $summary['sla_total']++;
                $summary['entities'][$entity_name]['sla_total']++;

                $status = 'compliant';
                $is_violated = false;
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
                    $is_violated = true;
                    if ($tto_violated && $ttr_violated) {
                        $violation_type = 'TTO + TTR';
                        $summary['sla_tto_violated']++;
                        $summary['sla_ttr_violated']++;
                        $summary['entities'][$entity_name]['sla_tto_violated']++;
                        $summary['entities'][$entity_name]['sla_ttr_violated']++;
                    } elseif ($tto_violated) {
                        $violation_type = 'TTO';
                        $summary['sla_tto_violated']++;
                        $summary['entities'][$entity_name]['sla_tto_violated']++;
                    } else {
                        $violation_type = 'TTR';
                        $summary['sla_ttr_violated']++;
                        $summary['entities'][$entity_name]['sla_ttr_violated']++;
                    }
                }

                $status_key = ($status == 'violated' ? 'violated' : ($status == 'active' ? 'active' : 'ok'));
                $summary['sla_' . $status_key]++;
                $summary['entities'][$entity_name]['sla_' . $status_key]++;

                $status_label = ($status == 'violated' ? __('Violated', 'slareport') : ($status == 'active' ? __('Active', 'slareport') : __('Compliant', 'slareport')));
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
                'pending_seconds' => $pending_times[$ticket['id']] ?? 0,
                'pending_formatted' => self::formatInterval($pending_times[$ticket['id']] ?? 0),
                'pending_ratio' => 0,
                'breach_probability' => 0
            ];

            // Calculate Pending Ratio and Breach Probability
            $ttr_seconds = 0;
            if ($sla_ttr_id > 0 && isset($slas[$sla_ttr_id])) {
                $sla_ttr = $slas[$sla_ttr_id];
                $ttr_seconds = self::convertToSeconds($sla_ttr['number_time'], $sla_ttr['definition_time']);
            }

            if ($ttr_seconds > 0) {
                $p_seconds = $pending_times[$ticket['id']] ?? 0;
                $ratio = $p_seconds / $ttr_seconds;
                $prob = min(100, round($ratio * 100, 1));

                // Update the last added ticket in the array
                $idx = count($tickets) - 1;
                $tickets[$idx]['pending_ratio'] = $ratio;
                $tickets[$idx]['breach_probability'] = $prob;
            }
        }

        return [
            'summary' => $summary,
            'tickets' => $tickets
        ];
    }

    /**
     * Calculate total time spent in Pending status for a batch of tickets
     */
    static function calculateTotalPendingTime(array $ticket_ids)
    {
        global $DB;
        if (empty($ticket_ids)) {
            return [];
        }

        $pending_data = [];
        
        // GLPI 11 uses itemtype, items_id, new_value, old_value, date_mod in glpi_logs
        $logs = $DB->request([
            'SELECT' => ['id', 'items_id', 'date_mod', 'new_value', 'old_value'],
            'FROM'   => 'glpi_logs',
            'WHERE'  => [
                'itemtype'         => 'Ticket',
                'items_id'         => $ticket_ids,
                'id_search_option' => 12 // Status field for Tickets
            ],
            'ORDER'  => 'date_mod ASC'
        ]);

        $ticket_intervals = [];
        foreach ($logs as $log) {
            $tid = $log['items_id'];
            if (!isset($ticket_intervals[$tid])) {
                $ticket_intervals[$tid] = ['total' => 0, 'last_start' => null];
            }

            if ($log['new_value'] == CommonITILObject::WAITING) {
                $ticket_intervals[$tid]['last_start'] = $log['date_mod'];
            } elseif ($log['old_value'] == CommonITILObject::WAITING && $ticket_intervals[$tid]['last_start']) {
                $start = strtotime($ticket_intervals[$tid]['last_start']);
                $end = strtotime($log['date_mod']);
                if ($end > $start) {
                    $ticket_intervals[$tid]['total'] += ($end - $start);
                }
                $ticket_intervals[$tid]['last_start'] = null;
            }
        }

        // Add current pending time for tickets still in pending
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
            if (isset($ticket_intervals[$tid]) && $ticket_intervals[$tid]['last_start']) {
                $start = strtotime($ticket_intervals[$tid]['last_start']);
                if ($now > $start) {
                    $ticket_intervals[$tid]['total'] += ($now - $start);
                }
            }
        }

        foreach ($ticket_ids as $id) {
            $pending_data[$id] = $ticket_intervals[$id]['total'] ?? 0;
        }

        return $pending_data;
    }

    /**
     * Convert SLA time to seconds
     */
    static function convertToSeconds($number, $definition)
    {
        switch ($definition) {
            case 'minute':
                return $number * 60;
            case 'hour':
                return $number * 3600;
            case 'day':
                return $number * 86400;
            default:
                return $number * 3600;
        }
    }

    /**
     * Format seconds to human readable string (e.g. 2s 15d)
     */
    static function formatInterval($seconds)
    {
        if ($seconds <= 0)
            return "-";

        $h = floor($seconds / 3600);
        $m = floor(($seconds % 3600) / 60);

        if ($h > 0) {
            return sprintf(__('%1$d h %2$d m', 'slareport'), $h, $m);
        }
        return sprintf(__('%1$d m', 'slareport'), $m);
    }
}
