<?php
include("../../../inc/includes.php");

Session::checkLoginUser();

// Robust class include
include_once(GLPI_ROOT . "/plugins/slareport/inc/report.class.php");

$report = new PluginSlareportReport();

$start_date = $_GET['start_date'] ?? $_POST['start_date'] ?? date('Y-m-01');
$end_date   = $_GET['end_date'] ?? $_POST['end_date'] ?? date('Y-m-d');
$entity_id  = (int)($_GET['entity_id'] ?? $_POST['entity_id'] ?? 0);

$allowed_sorts = [
    'glpi_tickets.id',
    'glpi_tickets.name',
    'glpi_entities.completename',
    'glpi_tickets.date'
];

if (isset($_GET['sort']) && in_array($_GET['sort'], $allowed_sorts)) {
    $sort = $_GET['sort'];
} else {
    $sort = 'glpi_tickets.id';
}

if (isset($_GET['order']) && strtoupper($_GET['order']) === 'ASC') {
    $order = 'ASC';
} else {
    $order = 'DESC';
}

// Helper for sort links
if (!function_exists('getSortLink')) {
    function getSortLink($col, $current_sort, $current_order, $start, $end, $ent)
    {
        $new_order = ($current_sort == $col && $current_order == 'ASC') ? 'DESC' : 'ASC';
        return "?sort=$col&order=$new_order&start_date=$start&end_date=$end&entity_id=$ent";
    }
}

// CSV Export Logic
if (isset($_POST['export_csv']) || isset($_GET['export_csv'])) {
    // Clear any previous output to prevent corrupting CSV
    if (ob_get_length()) {
        ob_end_clean();
    }
    
    $data = PluginSlareportReport::getSlaComplianceData($start_date, $end_date, $entity_id, $sort, $order);
    $tickets = $data['tickets'];

    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename=sla_raporu_' . $start_date . '_' . $end_date . '.csv');

    $output = fopen('php://output', 'w');
    fprintf($output, chr(0xEF) . chr(0xBB) . chr(0xBF)); // UTF-8 BOM
    fputcsv($output, [
        PluginSlareportReport::trans('SLA_ID'),
        PluginSlareportReport::trans('SLA_Subject'),
        PluginSlareportReport::trans('SLA_Entity'),
        PluginSlareportReport::trans('SLA_Opening_Date'),
        PluginSlareportReport::trans('SLA_Status'),
        PluginSlareportReport::trans('SLA_Violation_Type'),
        PluginSlareportReport::trans('SLA_Definition'),
        PluginSlareportReport::trans('SLA_Pending_Time'),
        PluginSlareportReport::trans('SLA_Pending_Reason'),
        PluginSlareportReport::trans('SLA_Risk_Level'),
        PluginSlareportReport::trans('SLA_Audit_Flags'),
        PluginSlareportReport::trans('SLA_TTO_Deadline'),
        PluginSlareportReport::trans('SLA_TTR_Deadline'),
        PluginSlareportReport::trans('SLA_Resolution_Date'),
        PluginSlareportReport::trans('SLA_TTO_Delay'),
        PluginSlareportReport::trans('SLA_TTR_Delay')
    ]);

    foreach ($tickets as $ticket) {
        fputcsv($output, [
            $ticket['id'],
            $ticket['name'],
            $ticket['entity'],
            $ticket['date'],
            $ticket['status_label'],
            $ticket['violation_type'] ?: '-',
            $ticket['sla_name'] ?: '-',
            $ticket['pending_formatted'] ?: '-',
            $ticket['pending_reason'] ?: '-',
            strtoupper($ticket['audit']['risk_level']),
            implode(', ', $ticket['audit']['flags']) ?: 'NONE',
            ($ticket['status'] == 'none' ? '-' : $ticket['tto_deadline']),
            ($ticket['status'] == 'none' ? '-' : $ticket['ttr_deadline']),
            $ticket['solvedate'],
            ($ticket['status'] == 'none' ? '-' : $ticket['tto_delay_formatted']),
            ($ticket['status'] == 'none' ? '-' : $ticket['solve_delay_formatted'])
        ]);
    }
    
    fputcsv($output, []);
    fputcsv($output, [PluginSlareportReport::trans('SLA_Audit_Legend')]);
    fputcsv($output, [PluginSlareportReport::trans('SLA_HIGH_RISK'), PluginSlareportReport::trans('SLA_HIGH_DESC')]);
    fputcsv($output, [PluginSlareportReport::trans('SLA_SUSPICIOUS'), PluginSlareportReport::trans('SLA_SUSP_DESC')]);
    fputcsv($output, [PluginSlareportReport::trans('SLA_NORMAL'), PluginSlareportReport::trans('SLA_NORM_DESC')]);
    fputcsv($output, []);
    fputcsv($output, [PluginSlareportReport::trans('SLA_Risk_Flags')]);
    fputcsv($output, ['stagnant', PluginSlareportReport::trans('SLA_Flag_Stagnant')]);
    fputcsv($output, ['last_minute', PluginSlareportReport::trans('SLA_Flag_LastMinute')]);
    fputcsv($output, ['excessive_toggling', PluginSlareportReport::trans('SLA_Flag_Toggling')]);

    fclose($output);
    exit;
}

Html::header(PluginSlareportReport::trans('SLA_Report_Title'), $_SERVER['PHP_SELF'], "tools", "plugins");

$data = PluginSlareportReport::getSlaComplianceData($start_date, $end_date, $entity_id, $sort, $order);
$summary = $data['summary'];
$tickets = $data['tickets'];

$compliance_rate = ($summary['sla_total'] > 0) ? round(($summary['sla_ok'] / $summary['sla_total']) * 100, 1) : 0;
?>

<style>
    :root {
        --primary: #4f46e5;
        --success: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --info: #3b82f6;
        --bg: #f8fafc;
        --card-bg: #ffffff;
        --text: #1e293b;
        --text-muted: #64748b;
    }

    .dashboard-container {
        padding: 24px;
        background: var(--bg);
        font-family: 'Inter', system-ui, sans-serif;
    }

    .dashboard-header {
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .dashboard-header h2 {
        margin: 0;
        font-size: 20px;
        color: var(--text);
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .version-badge {
        background: #f1f5f9;
        color: var(--text-muted);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }

    .filter-form {
        background: var(--card-bg);
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 24px;
        border: 1px solid #e2e8f0;
        display: flex;
        flex-wrap: nowrap;
        gap: 12px;
        align-items: flex-end;
    }

    .filter-group {
        display: flex;
        flex-direction: column;
        gap: 4px;
        min-width: 140px;
    }

    .filter-group label {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-muted);
    }

    .submit-btn {
        background: var(--primary);
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        font-size: 13px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }

    .kpi-container {
        display: flex;
        gap: 10px;
        margin-bottom: 24px;
    }

    .kpi-card {
        flex: 1;
        background: var(--card-bg);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
        text-align: center;
    }

    .kpi-value {
        font-size: 22px;
        font-weight: 700;
        color: var(--text);
    }

    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
    }

    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        color: white;
        text-transform: uppercase;
    }

    .chart-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }

    .chart-card {
        background: var(--card-bg);
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
        height: 300px;
    }

    .tab_cadre_fixehov {
        width: 100% !important;
        background: white;
    }

    .audit-badge {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
    }
    .audit-high { background: #fee2e2; color: #991b1b; }
    .audit-suspicious { background: #fef3c7; color: #92400e; }
    .audit-normal { background: #ecfdf5; color: #065f46; }
    
    .flag-icon {
        display: inline-block;
        margin-left: 4px;
        cursor: help;
    }
</style>

<div class='dashboard-container'>
    <div class='dashboard-header'>
        <h2><?php echo PluginSlareportReport::trans('SLA_Report_Title'); ?> <span class='version-badge'>v<?php echo PLUGIN_SLAREPORT_VERSION; ?> [Stable]</span></h2>
    </div>

    <form method='get' action='' class='filter-form'>
        <div class='filter-group'>
            <label><?php echo PluginSlareportReport::trans('SLA_Start_Date'); ?></label>
            <?php Html::showDateField('start_date', ['value' => $start_date]); ?>
        </div>
        <div class='filter-group'>
            <label><?php echo PluginSlareportReport::trans('SLA_End_Date'); ?></label>
            <?php Html::showDateField('end_date', ['value' => $end_date]); ?>
        </div>
        <div class='filter-group'>
            <label><?php echo PluginSlareportReport::trans('SLA_Entity'); ?></label>
            <?php
            Entity::dropdown([
                'name'                => 'entity_id',
                'value'               => $entity_id,
                'is_recursive'        => true,
                'display_emptychoice' => true,
                'emptylabel'          => PluginSlareportReport::trans('SLA_All'),
                'width'               => '100%'
            ]);
            ?>
        </div>
        <div class='btn-group' style='display: flex; gap: 8px; margin-left: auto;'>
            <input type='submit' value="<?php echo PluginSlareportReport::trans('SLA_Search'); ?>" class='submit-btn'>
            <input type='submit' name='export_csv' value="<?php echo PluginSlareportReport::trans('SLA_CSV'); ?>" class='submit-btn' style='background: var(--success)'>
            <button type='button' class='submit-btn' style='background: var(--danger)' onclick="window.open('export_pdf.php?start_date=' + encodeURIComponent(document.getElementsByName('start_date')[0].value) + '&end_date=' + encodeURIComponent(document.getElementsByName('end_date')[0].value) + '&entity_id=' + document.getElementsByName('entity_id')[0].value, '_blank')">
                <i class='fas fa-file-pdf'></i> <?php echo PluginSlareportReport::trans('SLA_PDF'); ?>
            </button>
        </div>
    </form>

    <div class='kpi-container'>
        <div class='kpi-card'>
            <div class='kpi-value'><?php echo $summary['total_tickets']; ?></div>
            <div class='kpi-label'><?php echo PluginSlareportReport::trans('SLA_Total_Tickets'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--primary)'><?php echo $summary['sla_total']; ?></div>
            <div class='kpi-label'><?php echo PluginSlareportReport::trans('SLA_SLA_Tickets'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--success)'><?php echo $compliance_rate; ?>%</div>
            <div class='kpi-label'><?php echo PluginSlareportReport::trans('SLA_Compliance'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--danger)'><?php echo $summary['sla_violated']; ?></div>
            <div class='kpi-label'><?php echo PluginSlareportReport::trans('SLA_Breaches'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--warning)'><?php echo $summary['sla_waiting']; ?></div>
            <div class='kpi-label'><?php echo PluginSlareportReport::trans('SLA_Pending_Label'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--info)'><?php echo $summary['sla_active']; ?></div>
            <div class='kpi-label'><?php echo PluginSlareportReport::trans('SLA_Active_SLAs'); ?></div>
        </div>
    </div>

    <div class='chart-grid'>
        <div class='chart-card'>
            <h3><?php echo PluginSlareportReport::trans('SLA_Status_Distribution'); ?></h3>
            <canvas id='complianceChart'></canvas>
        </div>
        <div class='chart-card'>
            <h3><?php echo PluginSlareportReport::trans('SLA_Top_Entities'); ?></h3>
            <canvas id='violationsChart'></canvas>
        </div>
    </div>

    <table class='tab_cadre_fixehov'>
        <tr>
            <th><a href="<?php echo getSortLink('glpi_tickets.id', $sort, $order, $start_date, $end_date, $entity_id); ?>"><?php echo PluginSlareportReport::trans('SLA_ID'); ?></a></th>
            <th style='width: 30%'><a href="<?php echo getSortLink('glpi_tickets.name', $sort, $order, $start_date, $end_date, $entity_id); ?>"><?php echo PluginSlareportReport::trans('SLA_Subject'); ?></a></th>
            <th><a href="<?php echo getSortLink('glpi_entities.completename', $sort, $order, $start_date, $end_date, $entity_id); ?>"><?php echo PluginSlareportReport::trans('SLA_Entity'); ?></a></th>
            <th><a href="<?php echo getSortLink('glpi_tickets.date', $sort, $order, $start_date, $end_date, $entity_id); ?>"><?php echo PluginSlareportReport::trans('SLA_Opening_Date'); ?></a></th>
            <th><?php echo PluginSlareportReport::trans('SLA_Status'); ?></th>
            <th><?php echo PluginSlareportReport::trans('SLA_Violation'); ?></th>
            <th><?php echo PluginSlareportReport::trans('SLA_Definition'); ?></th>
            <th><?php echo PluginSlareportReport::trans('SLA_Pending_Time'); ?></th>
            <th><?php echo PluginSlareportReport::trans('SLA_Reason'); ?></th>
            <th><?php echo PluginSlareportReport::trans('SLA_Audit_Risk'); ?></th>
            <th><?php echo PluginSlareportReport::trans('SLA_Deadline'); ?></th>
        </tr>
        <?php foreach ($tickets as $ticket):
            $pending_bg = 'transparent';
            if ($ticket['pending_ratio'] > 0.7) { $pending_bg = 'var(--warning)'; }
            elseif ($ticket['pending_ratio'] > 0.3) { $pending_bg = '#fef3c7'; }
        ?>
            <tr class='tab_bg_1'>
                <td><a href='/front/ticket.form.php?id=<?php echo $ticket['id']; ?>' target='_blank'><strong>#<?php echo $ticket['id']; ?></strong></a></td>
                <td><?php echo $ticket['name']; ?></td>
                <td><?php echo $ticket['entity']; ?></td>
                <td><?php echo $ticket['date']; ?></td>
                <td>
                    <span class='badge' style='background: <?php echo ($ticket['status'] == 'violated' ? 'var(--danger)' : ($ticket['status'] == 'active' ? 'var(--info)' : 'var(--success)')); ?>'>
                        <?php echo $ticket['status_label']; ?>
                    </span>
                </td>
                <td><strong><?php echo $ticket['violation_type'] ?: '-'; ?></strong></td>
                <td><?php echo $ticket['sla_name'] ?: '-'; ?></td>
                <td style='text-align: center; background: <?php echo $pending_bg; ?>'>
                    <strong><?php echo $ticket['pending_formatted']; ?></strong>
                </td>
                <td><small><?php echo $ticket['pending_reason']; ?></small></td>
                <td>
                    <span class="audit-badge audit-<?php echo $ticket['audit']['risk_level']; ?>">
                        <?php 
                        if ($ticket['audit']['risk_level'] == 'high') echo '⚠️ ' . PluginSlareportReport::trans('SLA_HIGH_RISK');
                        elseif ($ticket['audit']['risk_level'] == 'suspicious') echo '🧐 ' . PluginSlareportReport::trans('SLA_SUSPICIOUS');
                        else echo '✅ ' . PluginSlareportReport::trans('SLA_NORMAL');
                        ?>
                    </span>
                    <div style="margin-top: 4px;">
                        <?php foreach ($ticket['audit']['flags'] as $flag): ?>
                            <span class="flag-icon" title="<?php 
                                switch($flag) {
                                    case 'stagnant': echo PluginSlareportReport::trans('SLA_Flag_Stagnant'); break;
                                    case 'last_minute': echo PluginSlareportReport::trans('SLA_Flag_LastMinute'); break;
                                    case 'excessive_toggling': echo PluginSlareportReport::trans('SLA_Flag_Toggling'); break;
                                }
                            ?>">
                                <?php 
                                switch($flag) {
                                    case 'stagnant': echo '🛑'; break;
                                    case 'last_minute': echo '⏰'; break;
                                    case 'excessive_toggling': echo '🔄'; break;
                                }
                                ?>
                            </span>
                        <?php endforeach; ?>
                    </div>
                </td>
                <td>
                    <?php if ($ticket['status'] != 'none'): ?>
                        TTO: <?php echo Html::convDateTime($ticket['tto_deadline']); ?><br>
                        TTR: <?php echo Html::convDateTime($ticket['ttr_deadline']); ?>
                    <?php else: ?>
                        -
                    <?php endif; ?>
                </td>
            </tr>
        <?php endforeach; ?>
    </table>
</div>

<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
<script>
    new Chart(document.getElementById('complianceChart'), {
        type: 'doughnut',
        data: {
            labels: [
                "<?php echo PluginSlareportReport::trans('SLA_Compliant_Label'); ?>",
                "<?php echo PluginSlareportReport::trans('SLA_Violated_Label'); ?>",
                "<?php echo PluginSlareportReport::trans('SLA_Active_Label'); ?>",
                "<?php echo PluginSlareportReport::trans('SLA_Pending_Label'); ?>"
            ],
            datasets: [{
                data: [
                    <?php echo $summary['sla_ok']; ?>, 
                    <?php echo $summary['sla_violated']; ?>, 
                    <?php echo $summary['sla_active']; ?>,
                    <?php echo $summary['sla_waiting']; ?>
                ],
                backgroundColor: ['#10b981', '#ef4444', '#3b82f6', '#f59e0b'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });

    <?php
    $violations_by_entity = [];
    foreach ($summary['entities'] as $name => $stats) {
        if (isset($stats['sla_violated']) && $stats['sla_violated'] > 0) {
            $violations_by_entity[$name] = $stats['sla_violated'];
        }
    }
    arsort($violations_by_entity);
    $top_violations = array_slice($violations_by_entity, 0, 10);
    ?>
    new Chart(document.getElementById('violationsChart'), {
        type: 'bar',
        data: {
            labels: <?php echo json_encode(array_keys($top_violations)); ?>,
            datasets: [{
                label: "<?php echo PluginSlareportReport::trans('SLA_Breaches'); ?>",
                data: <?php echo json_encode(array_values($top_violations)); ?>,
                backgroundColor: '#ef4444'
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
</script>
<?php Html::footer(); ?>