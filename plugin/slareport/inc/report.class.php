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

        $slas = self::getSlaDefinitions();
        $entities = self::getEntities();

        $where = [
            'glpi_tickets.is_deleted' => 0,
            'AND' => [
                ['glpi_tickets.date' => ['>=', $start_date . ' 00:00:00']],
                ['glpi_tickets.date' => ['<=', $end_date . ' 23:59:59']]
            ]
        ];

        if ($entity_id > 0) {
            $where['glpi_tickets.entities_id'] = $entity_id;
        }

        $iterator = $DB->request([
            'SELECT' => [
                'glpi_tickets.id',
                'glpi_tickets.name',
                'glpi_tickets.date',
                'glpi_tickets.status',
                'glpi_tickets.solvedate',
                'glpi_tickets.time_to_resolve',
                'glpi_tickets.time_to_own',
                'glpi_tickets.solve_delay_stat',
                'glpi_tickets.entities_id',
                'glpi_tickets.slas_id_ttr',
                'glpi_tickets.slas_id_tto',
                'glpi_tickets.takeintoaccount_delay_stat'
            ],
            'FROM' => 'glpi_tickets',
            'WHERE' => $where,
            'ORDER' => "$sort $order"
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

        foreach ($iterator as $ticket) {
            $summary['total_tickets']++;
            $entity_id_ticket = (int)$ticket['entities_id'];
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

            $sla_ttr_id = (int)$ticket['slas_id_ttr'];
            $sla_tto_id = (int)$ticket['slas_id_tto'];

            if ($sla_ttr_id == 0 && $sla_tto_id == 0) {
                // Non-SLA Ticket
                $summary['sla_none']++;
                $summary['entities'][$entity_name]['sla_none']++;
                $status = 'none';
                $status_label = __('SLA Not Defined', 'slareport');
                $violation_type = '';
            }
            else {
                // SLA Ticket
                $summary['sla_total']++;
                $summary['entities'][$entity_name]['sla_total']++;

                $status = 'compliant';
                $is_violated = false;
                $violation_type = '';

                // TTR Calculation
                $ttr_violated = false;
                if ($sla_ttr_id > 0 && isset($slas[$sla_ttr_id])) {
                    $sla = $slas[$sla_ttr_id];
                    $limit = self::convertToSeconds($sla['number_time'], $sla['definition_time']);
                    $delay = (int)$ticket['solve_delay_stat'];

                    if ($delay > 0 && $delay > $limit) {
                        $ttr_violated = true;
                    }
                    elseif ($ticket['status'] < 5 && !empty($ticket['time_to_resolve'])) {
                        if ($current_time > $ticket['time_to_resolve']) {
                            $ttr_violated = true;
                        }
                        else {
                            $status = 'active';
                        }
                    }
                }

                // TTO Calculation
                $tto_violated = false;
                if ($sla_tto_id > 0 && isset($slas[$sla_tto_id])) {
                    $sla = $slas[$sla_tto_id];
                    $limit = self::convertToSeconds($sla['number_time'], $sla['definition_time']);
                    $tto_delay = (int)$ticket['takeintoaccount_delay_stat'];

                    if ($tto_delay > 0 && $tto_delay > $limit) {
                        $tto_violated = true;
                    }
                    elseif ($ticket['status'] == 1 && !empty($ticket['time_to_own'])) {
                        if ($current_time > $ticket['time_to_own']) {
                            $tto_violated = true;
                        }
                        else {
                            $status = 'active';
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
                    }
                    elseif ($tto_violated) {
                        $violation_type = 'TTO';
                        $summary['sla_tto_violated']++;
                        $summary['entities'][$entity_name]['sla_tto_violated']++;
                    }
                    else {
                        $violation_type = 'TTR';
                        $summary['sla_ttr_violated']++;
                        $summary['entities'][$entity_name]['sla_ttr_violated']++;
                    }
                }

                // Global and Entity Summaries for SLA status
                $status_key = ($status == 'violated' ? 'violated' : ($status == 'active' ? 'active' : 'ok'));
                $summary['sla_' . $status_key]++;
                $summary['entities'][$entity_name]['sla_' . $status_key]++;
                $status_label = ($status == 'violated' ? __('Violated', 'slareport') : ($status == 'active' ? __('Active', 'slareport') : __('Compliant', 'slareport')));
            }

            // Add to ticket list
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
                'sla_name' => (isset($slas[$ticket['slas_id_ttr']]) ? $slas[$ticket['slas_id_ttr']]['name'] : '')
                . (isset($slas[$ticket['slas_id_tto']]) ? ' / ' . $slas[$ticket['slas_id_tto']]['name'] : '')
            ];
        }

        return [
            'summary' => $summary,
            'tickets' => $tickets
        ];
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
