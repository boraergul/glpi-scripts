<?php
include("../../../inc/includes.php");

Session::checkLoginUser();

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
    $sort = 'glpi_tickets.date';
}

if (isset($_GET['order']) && strtoupper($_GET['order']) === 'ASC') {
    $order = 'ASC';
} else {
    $order = 'DESC';
}

// CSV Export Logic
if (isset($_POST['export_csv']) || isset($_GET['export_csv'])) {
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
        __('Opening Date', 'slareport'),
        __('Status', 'slareport'),
        __('Violation Type', 'slareport'),
        __('SLA Definition', 'slareport'),
        __('Pending Time', 'slareport'),
        __('Pending Reason', 'slareport'),
        __('Risk Level', 'slareport'),
        __('Audit Flags', 'slareport'),
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
    
    // Add Legend rows at the end of CSV
    fputcsv($output, []); // Empty row
    fputcsv($output, ['SLA Audit Legend / Denetim Sözlüğü']);
    fputcsv($output, ['HIGH RISK', 'SLA manipülasyonu belirtileri (Yüksek Risk)']);
    fputcsv($output, ['SUSPICIOUS', 'Olağandışı kullanım örüntüleri (Şüpheli)']);
    fputcsv($output, ['NORMAL', 'Kurallara uygun yönetim']);
    fputcsv($output, []);
    fputcsv($output, ['Risk Flags / Risk Bayrakları']);
    fputcsv($output, ['stagnant', 'Bekleme süresi SLA süresini aşmış (Durağan)']);
    fputcsv($output, ['last_minute', 'SLA bitimine %10 kala beklemeye alınmış (Son Dakika)']);
    fputcsv($output, ['excessive_toggling', '3 kereden fazla beklemeye al/çıkar yapılmış (Aşırı Git-Gel)']);

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
        <h2><?php echo __('SLA Breach Report', 'slareport'); ?> <span class='version-badge'>v<?php echo PLUGIN_SLAREPORT_VERSION; ?> [Stable]</span></h2>
    </div>

    <form method='get' action='' class='filter-form'>
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
            <?php
            Entity::dropdown([
                'name'                => 'entity_id',
                'value'               => $entity_id,
                'is_recursive'        => true,
                'display_emptychoice' => true,
                'emptylabel'          => __('All', 'slareport'),
                'width'               => '100%'
            ]);
            ?>
        </div>
        <div class='btn-group' style='display: flex; gap: 8px; margin-left: auto;'>
            <input type='submit' value="<?php echo __s('Search', 'slareport'); ?>" class='submit-btn'>
            <input type='submit' name='export_csv' value="<?php echo __s('CSV', 'slareport'); ?>" class='submit-btn' style='background: var(--success)'>
            <button type='button' class='submit-btn' style='background: var(--danger)' onclick="window.open('export_pdf.php?start_date=' + encodeURIComponent(document.getElementsByName('start_date')[0].value) + '&end_date=' + encodeURIComponent(document.getElementsByName('end_date')[0].value) + '&entity_id=' + document.getElementsByName('entity_id')[0].value, '_blank')">
                <i class='fas fa-file-pdf'></i> <?php echo __s('PDF', 'slareport'); ?>
            </button>
        </div>
    </form>

    <div class='kpi-container'>
        <div class='kpi-card'>
            <div class='kpi-value'><?php echo $summary['total_tickets']; ?></div>
            <div class='kpi-label'><?php echo __('Total Tickets', 'slareport'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--primary)'><?php echo $summary['sla_total']; ?></div>
            <div class='kpi-label'><?php echo __('SLA Tickets', 'slareport'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--success)'><?php echo $compliance_rate; ?>%</div>
            <div class='kpi-label'><?php echo __('SLA Compliance', 'slareport'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--danger)'><?php echo $summary['sla_violated']; ?></div>
            <div class='kpi-label'><?php echo __('Breaches', 'slareport'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--warning)'><?php echo $summary['sla_waiting']; ?></div>
            <div class='kpi-label'><?php echo __('Pending', 'slareport'); ?></div>
        </div>
        <div class='kpi-card'>
            <div class='kpi-value' style='color: var(--info)'><?php echo $summary['sla_active']; ?></div>
            <div class='kpi-label'><?php echo __('Active SLAs', 'slareport'); ?></div>
        </div>
    </div>

    <div class='chart-grid'>
        <div class='chart-card'>
            <h3><?php echo __('SLA Status Distribution', 'slareport'); ?></h3>
            <canvas id='complianceChart'></canvas>
        </div>
        <div class='chart-card'>
            <h3><?php echo __('Top Violating Entities', 'slareport'); ?></h3>
            <canvas id='violationsChart'></canvas>
        </div>
    </div>

    <table class='tab_cadre_fixehov'>
        <tr>
            <th><a href="<?php echo getSortLink('glpi_tickets.id', $sort, $order, $start_date, $end_date, $entity_id); ?>">ID</a></th>
            <th style='width: 30%'><a href="<?php echo getSortLink('glpi_tickets.name', $sort, $order, $start_date, $end_date, $entity_id); ?>"><?php echo __('Subject', 'slareport'); ?></a></th>
            <th><a href="<?php echo getSortLink('glpi_entities.completename', $sort, $order, $start_date, $end_date, $entity_id); ?>"><?php echo __('Entity', 'slareport'); ?></a></th>
            <th><a href="<?php echo getSortLink('glpi_tickets.date', $sort, $order, $start_date, $end_date, $entity_id); ?>"><?php echo __('Opening Date', 'slareport'); ?></a></th>
            <th><?php echo __('Status', 'slareport'); ?></th>
            <th><?php echo __('Violation', 'slareport'); ?></th>
            <th><?php echo __('SLA Definition', 'slareport'); ?></th>
            <th><?php echo __('Pending Time', 'slareport'); ?></th>
            <th><?php echo __('Reason', 'slareport'); ?></th>
            <th><?php echo __('Audit / Risk', 'slareport'); ?></th>
            <th><?php echo __('Deadline', 'slareport'); ?></th>
        </tr>
        <?php foreach ($tickets as $ticket):
            // Calculate styles for pending metrics
            $pending_bg = 'transparent';
            if ($ticket['pending_ratio'] > 0.7) {
                $pending_bg = 'var(--warning)';
            } elseif ($ticket['pending_ratio'] > 0.3) {
                $pending_bg = '#fef3c7';
            }

            $pending_color = 'var(--text)';
            if ($ticket['pending_ratio'] > 1) {
                $pending_color = 'var(--danger)';
            } elseif ($ticket['pending_ratio'] > 0.7) {
                $pending_color = 'var(--warning)';
            }
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
                        if ($ticket['audit']['risk_level'] == 'high') echo '⚠️ ' . __('HIGH RISK', 'slareport');
                        elseif ($ticket['audit']['risk_level'] == 'suspicious') echo '🧐 ' . __('SUSPICIOUS', 'slareport');
                        else echo '✅ ' . __('NORMAL', 'slareport');
                        ?>
                    </span>
                    <div style="margin-top: 4px;">
                        <?php foreach ($ticket['audit']['flags'] as $flag): ?>
                            <span class="flag-icon" title="<?php 
                                switch($flag) {
                                    case 'stagnant': echo __('Pending time exceeds TTR limit', 'slareport'); break;
                                    case 'last_minute': echo __('Moved to pending at the last minute of SLA', 'slareport'); break;
                                    case 'excessive_toggling': echo __('Frequent status changes to/from Pending', 'slareport'); break;
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
    // Compliance Chart
    new Chart(document.getElementById('complianceChart'), {
        type: 'doughnut',
        data: {
            labels: [
                "<?php echo __s('Compliant', 'slareport'); ?>",
                "<?php echo __s('Violated', 'slareport'); ?>",
                "<?php echo __s('Active', 'slareport'); ?>",
                "<?php echo __s('Pending', 'slareport'); ?>"
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

    // Violations Chart
    <?php
    $violations_by_entity = [];
    foreach ($summary['entities'] as $name => $stats) {
        if ($stats['sla_violated'] > 0) {
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
                label: "<?php echo __s('Breaches', 'slareport'); ?>",
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