<?php

include("../../../inc/includes.php");

Session::checkLoginUser();

$report = new PluginSlareportReport();

$start_date = isset($_POST['start_date']) ? $_POST['start_date'] : (isset($_GET['start_date']) ? $_GET['start_date'] : date('Y-m-01'));
$end_date = isset($_POST['end_date']) ? $_POST['end_date'] : (isset($_GET['end_date']) ? $_GET['end_date'] : date('Y-m-d'));
$entity_id = isset($_POST['entity_id']) ? (int)$_POST['entity_id'] : (isset($_GET['entity_id']) ? (int)$_GET['entity_id'] : 0);

$sort = isset($_GET['sort']) ? $_GET['sort'] : 'glpi_tickets.date';
$order = isset($_GET['order']) ? $_GET['order'] : 'DESC';

// CSV Export Logic
if (isset($_POST['export_csv'])) {
    $data = PluginSlareportReport::getSlaComplianceData($start_date, $end_date, $entity_id, $sort, $order);
    $tickets = $data['tickets'];

    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename=sla_raporu_' . $start_date . '_' . $end_date . '.csv');

    $output = fopen('php://output', 'w');
    fprintf($output, chr(0xEF) . chr(0xBB) . chr(0xBF)); // UTF-8 BOM
    fputcsv($output, [
        __('ID', 'slareport'),
        __('Subject', 'slareport'),
        __('Entity', 'slareport'),
        __('Date', 'slareport'),
        __('Status', 'slareport'),
        __('Violation Type', 'slareport'),
        __('SLA Definition', 'slareport'),
        __('TTO Deadline', 'slareport'),
        __('TTR Deadline', 'slareport'),
        __('Resolution Date', 'slareport'),
        __('TTO Delay', 'slareport'),
        __('TTR Delay', 'slareport')
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
            ($ticket['status'] == 'none' ? '-' : $ticket['tto_deadline']),
            ($ticket['status'] == 'none' ? '-' : $ticket['ttr_deadline']),
            $ticket['solvedate'],
            ($ticket['status'] == 'none' ? '-' : $ticket['tto_delay_formatted']),
            ($ticket['status'] == 'none' ? '-' : $ticket['solve_delay_formatted'])
        ]);
    }
    fclose($output);
    exit;
}

Html::header(__('SLA Breach Report', 'slareport'), $_SERVER['PHP_SELF'], "tools", "plugins");

$data = PluginSlareportReport::getSlaComplianceData($start_date, $end_date, $entity_id, $sort, $order);
$summary = $data['summary'];
$tickets = $data['tickets'];

$compliance_rate = ($summary['sla_total'] > 0) ? round(($summary['sla_ok'] / $summary['sla_total']) * 100, 1) : 0;

// Helper for sort links
function getSortLink($col, $current_sort, $current_order, $start, $end, $ent)
{
    $new_order = ($current_sort == $col && $current_order == 'ASC') ? 'DESC' : 'ASC';
    return "?sort=$col&order=$new_order&start_date=$start&end_date=$end&entity_id=$ent";
}

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

    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }

    .kpi-card {
        background: var(--card-bg);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: transform 0.2s;
    }

    .kpi-card:hover { transform: translateY(-4px); }

    .kpi-value { font-size: 28px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
    .kpi-label { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; }

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
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
        height: 350px;
    }

    .chart-card h3 { font-size: 16px; margin-bottom: 20px; color: var(--text); }

    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        color: white;
        text-transform: uppercase;
    }
    .badge-violated { background: var(--danger); }
    .badge-compliant { background: var(--success); }
    .badge-active { background: var(--info); }

    .filter-form {
        background: var(--card-bg);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid #e2e8f0;
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        align-items: flex-end;
    }

    .filter-group { display: flex; flex-direction: column; gap: 6px; }
    .filter-group label { font-size: 12px; font-weight: 600; color: var(--text-muted); }

    .submit-btn {
        background: var(--primary);
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .submit-btn:hover { opacity: 0.9; }

    .sort-icon { font-size: 10px; margin-left: 4px; opacity: 0.5; }
    th a { color: inherit; text-decoration: none; display: flex; align-items: center; }
    th a:hover { color: var(--primary); }

</style>

<div class='dashboard-container'>
    <form method='post' action='' class='filter-form'>
        <?php
if (method_exists('Html', 'printCSRFToken')) {
    Html::printCSRFToken();
}
else {
    echo "<input type='hidden' name='_glpi_csrf_token' value='" . Session::getNewCSRFToken() . "'>";
}
?>
        <div class='filter-group'>
            <label><?php echo __('Start Date', 'slareport'); ?></label>
            <?php Html::showDateField('start_date', ['value' => $start_date]); ?>
        </div>
        <div class='filter-group'>
            <label><?php echo __('End Date', 'slareport'); ?></label>
            <?php Html::showDateField('end_date', ['value' => $end_date]); ?>
        </div>
        <div class='filter-group'>
            <label><?php echo __('Entity', 'slareport'); ?></label>
            <select name='entity_id' class='select'>
                <option value='0'>--- <?php echo __('All', 'slareport'); ?> ---</option>
                <?php
$entities = PluginSlareportReport::getEntities();
foreach ($entities as $id => $name) {
    $selected = ($entity_id == $id) ? "selected" : "";
    echo "<option value='$id' $selected>$name</option>";
}
?>
            </select>
        </div>
        <input type='submit' name='submit' value="<?php echo __s('Search', 'slareport'); ?>" class='submit-btn'>
        <input type='submit' name='export_csv' value="<?php echo __s('Export to CSV', 'slareport'); ?>" class='submit-btn' style='background: var(--success)'>
    </form>

    <div class='kpi-container'>
        <div class='kpi-card'>
            <div class='kpi-value'><?php echo $summary['total_tickets']; ?></div>
            <div class='kpi-label'><?php echo __('Total Tickets', 'slareport'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value'><?php echo $summary['sla_total']; ?></div>
            <div class='kpi-label'><?php echo __('SLA Tickets', 'slareport'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--success)'><?php echo $summary['sla_ok']; ?></div>
            <div class='kpi-label'><?php echo __('SLA Compliant', 'slareport'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--danger)'><?php echo $summary['sla_tto_violated']; ?></div>
            <div class='kpi-label'><?php echo __('TTO Violated', 'slareport'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--danger)'><?php echo $summary['sla_ttr_violated']; ?></div>
            <div class='kpi-label'><?php echo __('TTR Violated', 'slareport'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--info)'><?php echo $summary['sla_active']; ?></div>
            <div class='kpi-label'><?php echo __('SLA Active', 'slareport'); ?></div>
        </div>
        <div class='kpi-card' style='background: var(--primary);'>
            <div class='kpi-value' style='color: white'><?php echo $compliance_rate; ?>%</div>
            <div class='kpi-label' style='color: rgba(255,255,255,0.7)'><?php echo __('SLA Compliance Rate', 'slareport'); ?></div>
        </div>
    </div>

    <div class='chart-grid'>
        <div class='chart-card'>
            <h3><?php echo __('Overall SLA Status', 'slareport'); ?></h3>
            <canvas id='complianceChart'></canvas>
        </div>
        <div class='chart-card'>
            <h3><?php echo __('Top Violating Entities (Top 10)', 'slareport'); ?></h3>
            <canvas id='violationsChart'></canvas>
        </div>
    </div>

    <table class='tab_cadre_fixehov'>
        <tr>
            <th><a href="<?php echo getSortLink('glpi_tickets.id', $sort, $order, $start_date, $end_date, $entity_id); ?>">ID <?php echo $sort == 'glpi_tickets.id' ? ($order == 'ASC' ? '↑' : '↓') : '↕'; ?></a></th>
            <th style='width: 35%'><a href="<?php echo getSortLink('glpi_tickets.name', $sort, $order, $start_date, $end_date, $entity_id); ?>"><?php echo __('Subject', 'slareport'); ?> <?php echo $sort == 'glpi_tickets.name' ? ($order == 'ASC' ? '↑' : '↓') : '↕'; ?></a></th>
            <th><a href="<?php echo getSortLink('glpi_entities.completename', $sort, $order, $start_date, $end_date, $entity_id); ?>"><?php echo __('Entity', 'slareport'); ?> <?php echo $sort == 'glpi_entities.completename' ? ($order == 'ASC' ? '↑' : '↓') : '↕'; ?></a></th>
            <th><a href="<?php echo getSortLink('glpi_tickets.date', $sort, $order, $start_date, $end_date, $entity_id); ?>"><?php echo __('Date', 'slareport'); ?> <?php echo $sort == 'glpi_tickets.date' ? ($order == 'ASC' ? '↑' : '↓') : '↕'; ?></a></th>
            <th><?php echo __('Status', 'slareport'); ?></th>
            <th><?php echo __('Violation', 'slareport'); ?></th>
            <th><?php echo __('SLA Definition', 'slareport'); ?></th>
            <th><?php echo __('Deadline', 'slareport'); ?></th>
            <th><?php echo __('Resolved', 'slareport'); ?></th>
            <th><?php echo __('Delay (TTO/TTR)', 'slareport'); ?></th>
        </tr>
        <?php if (empty($tickets)): ?>
            <tr><td colspan='10' class='center'><strong><?php echo __('No data found for the selected criteria.', 'slareport'); ?></strong></td></tr>
        <?php
else: ?>
            <?php foreach ($tickets as $ticket): ?>
                <tr class='tab_bg_1'>
                    <td><a href='/front/ticket.form.php?id=<?php echo $ticket['id']; ?>' target='_blank'><strong>#<?php echo $ticket['id']; ?></strong></a></td>
                    <td><?php echo $ticket['name']; ?></td>
                    <td><?php echo $ticket['entity']; ?></td>
                    <td><?php echo $ticket['date']; ?></td>
                    <td>
                        <?php
        if ($ticket['status'] == 'none') {
            echo "<span class='badge' style='background: #94a3b8'>" . $ticket['status_label'] . "</span>";
        }
        else {
            echo "<span class='badge' style='background: " . ($ticket['status'] == 'violated' ? 'var(--danger)' : ($ticket['status'] == 'active' ? 'var(--info)' : 'var(--success)')) . "'>" . $ticket['status_label'] . "</span>";
        }
?>
            </td>
            <td><strong><?php echo $ticket['violation_type'] ?: '-'; ?></strong></td>
            <td><?php echo $ticket['sla_name'] ?: '-'; ?></td>
            <td>
                <?php
        if ($ticket['status'] == 'none') {
            echo '-';
        }
        else {
            echo "TTO: " . Html::convDateTime($ticket['tto_deadline']) . "<br>";
            echo "TTR: " . Html::convDateTime($ticket['ttr_deadline']);
        }
?>
            </td>
            <td><?php echo Html::convDateTime($ticket['solvedate']); ?></td>
            <td>
                <?php
        if ($ticket['status'] == 'none') {
            echo '-';
        }
        else {
            echo "TTO: " . $ticket['tto_delay_formatted'] . "<br>";
            echo "TTR: " . $ticket['solve_delay_formatted'];
        }
?>
            </td>
        </tr>
            <?php
    endforeach; ?>
        <?php
endif; ?>
    </table>
</div>

<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
<script>
    // Compliance Chart
    new Chart(document.getElementById('complianceChart'), {
        type: 'doughnut',
        data: {
            labels: [
                "<?php echo __s('Compliant', 'slareport'); ?>", 
                "<?php echo __s('Violated', 'slareport'); ?>", 
                "<?php echo __s('Active', 'slareport'); ?>"
            ],
            datasets: [{
                data: [<?php echo $summary['sla_ok']; ?>, <?php echo $summary['sla_violated']; ?>, <?php echo $summary['sla_active']; ?>],
                backgroundColor: ['#10b981', '#ef4444', '#3b82f6'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    // Violations Chart
    <?php
$entity_violations = [];
foreach ($summary['entities'] as $name => $stats) {
    if ($stats['sla_violated'] > 0) {
        $entity_violations[$name] = $stats['sla_violated'];
    }
}
arsort($entity_violations);
$top_violations = array_slice($entity_violations, 0, 10);
?>
    
    new Chart(document.getElementById('violationsChart'), {
        type: 'bar',
        data: {
            labels: <?php echo json_encode(array_keys($top_violations)); ?>,
            datasets: [{
                label: "<?php echo __s('SLA Violated', 'slareport'); ?>",
                data: <?php echo json_encode(array_values($top_violations)); ?>,
                backgroundColor: '#ef4444',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
</script>

<?php Html::footer(); ?>
