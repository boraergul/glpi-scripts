<?php
include("../../../inc/includes.php");
Session::checkLoginUser();
global $DB;

$start_date  = $_GET['start_date'] ?? date('Y-m-01');
$end_date    = $_GET['end_date'] ?? date('Y-m-d');
$entities_id = isset($_GET['entity_id']) ? (int)$_GET['entity_id'] : 0;

$report = new PluginSlareportReport();
$data = PluginSlareportReport::getSlaComplianceData($start_date, $end_date, $entities_id);

$summary = $data['summary'];
$tickets = $data['tickets'];

$compliance_rate = ($summary['sla_total'] > 0) 
    ? round(($summary['sla_ok'] / $summary['sla_total']) * 100, 1) 
    : 100;

// Load TCPDF from GLPI Vendor
if (file_exists(GLPI_ROOT . '/vendor/autoload.php')) {
    require_once(GLPI_ROOT . '/vendor/autoload.php');
} elseif (file_exists(GLPI_ROOT . '/vendor/tecnickcom/tcpdf/tcpdf.php')) {
    require_once(GLPI_ROOT . '/vendor/tecnickcom/tcpdf/tcpdf.php');
}

class SlareportPDF extends \TCPDF {
    public function Header() {
        if ($this->getPage() > 1) {
            $this->SetY(8);
            $this->SetFont('dejavusans', 'I', 8);
            $this->SetTextColor(120, 120, 120);
            $this->Cell(0, 10, 'SLA Breach Report - ' . date('d.m.Y'), 0, 0, 'R');
            $this->Line(10, 16, $this->getPageWidth()-10, 16);
        }
    }
    public function Footer() {
        $this->SetY(-15);
        $this->SetFont('dejavusans', 'I', 8);
        $this->Cell(0, 10, 'Page '.$this->getAliasNumPage().'/'.$this->getAliasNbPages(), 0, false, 'C');
    }
}

$pdf = new SlareportPDF('L', 'mm', 'A4', true, 'UTF-8', false);
$pdf->SetCreator('GLPI Slareport Plugin');
$pdf->SetTitle('SLA Breach Report');
$pdf->SetMargins(10, 20, 10);
$pdf->SetAutoPageBreak(true, 20);

// --- COVER PAGE ---
$pdf->AddPage();
$pdf->SetFillColor(30, 41, 59); // Primary Slate
$pdf->Rect(0, 0, $pdf->getPageWidth(), $pdf->getPageHeight(), 'F');

$pdf->SetTextColor(255, 255, 255);
$pdf->SetY(60);
$pdf->SetFont('dejavusans', 'B', 32);
$pdf->Cell(0, 20, 'SLA BREACH REPORT', 0, 1, 'C');

$pdf->SetFont('dejavusans', '', 16);
$pdf->Cell(0, 15, $start_date . ' / ' . $end_date, 0, 1, 'C');

$pdf->SetY(120);
$pdf->SetFont('dejavusans', 'B', 14);
$pdf->Cell(0, 10, 'COMPLIANCE RATE: ' . $compliance_rate . '%', 0, 1, 'C');

$pdf->SetY(160);
$pdf->SetFont('dejavusans', '', 10);
$pdf->Cell(0, 10, 'Generated on: ' . date('d.m.Y H:i'), 0, 1, 'C');

// --- SUMMARY & CHARTS PAGE ---
$pdf->AddPage();
$pdf->SetTextColor(30, 41, 59);
$pdf->SetFont('dejavusans', 'B', 16);
$pdf->Cell(0, 15, '1. Executive Summary', 0, 1, 'L');

// KPI Table
$html_kpi = '
<table cellpadding="6" border="1" style="border-collapse:collapse; width:100%; background-color:#f8fafc;">
    <tr style="background-color:#1e293b; color:#ffffff; font-weight:bold;">
        <th align="center">Total Tickets</th>
        <th align="center">SLA Tickets</th>
        <th align="center">Compliant</th>
        <th align="center">Violated</th>
        <th align="center">Pending</th>
        <th align="center">Active</th>
        <th align="center">Compliance Rate</th>
    </tr>
    <tr>
        <td align="center">'.$summary['total_tickets'].'</td>
        <td align="center">'.$summary['sla_total'].'</td>
        <td align="center" style="color:#10b981; font-weight:bold;">'.$summary['sla_ok'].'</td>
        <td align="center" style="color:#ef4444; font-weight:bold;">'.$summary['sla_violated'].'</td>
        <td align="center" style="color:#f59e0b;">'.$summary['sla_waiting'].'</td>
        <td align="center" style="color:#3b82f6;">'.$summary['sla_active'].'</td>
        <td align="center" style="background-color:#4f46e5; color:#ffffff; font-weight:bold;">'.$compliance_rate.'%</td>
    </tr>
</table>';
$pdf->writeHTML($html_kpi, true, false, false, false, '');

$pdf->Ln(10);
$pdf->SetFont('dejavusans', 'B', 14);
$pdf->Cell(0, 15, '2. Violations by Entity (Top 10)', 0, 1, 'L');

$entity_violations = [];
foreach ($summary['entities'] as $name => $stats) {
    if ($stats['sla_violated'] > 0) {
        $entity_violations[$name] = $stats['sla_violated'];
    }
}
arsort($entity_violations);
$top_violations = array_slice($entity_violations, 0, 10);

if (empty($top_violations)) {
    $pdf->Cell(0, 10, 'No violations found.', 0, 1, 'L');
} else {
    $max_v = max($top_violations);
    $chart_html = '<table cellpadding="4" cellspacing="0" width="100%">';
    foreach ($top_violations as $name => $count) {
        $w = ($count / $max_v) * 70;
        $chart_html .= '<tr>
            <td width="20%" align="right"><strong>'.$name.'</strong></td>
            <td width="10%">'.$count.'</td>
            <td width="70%"><table width="'.$w.'%" border="0"><tr><td bgcolor="#ef4444" height="10"></td></tr></table></td>
        </tr>';
    }
    $chart_html .= '</table>';
    $pdf->writeHTML($chart_html, true, false, false, false, '');
}

// --- DETAILED TABLE ---
$pdf->AddPage();
$pdf->SetFont('dejavusans', 'B', 16);
$pdf->Cell(0, 15, '3. Detailed SLA Breach List', 0, 1, 'L');

$widths = [
    'id'        => '4%',
    'entity'    => '8%',
    'date'      => '8%',
    'title'     => '12%',
    'status'    => '7%',
    'sla'       => '10%',
    'pending'   => '12%',
    'audit'     => '10%',
    'deadlines' => '11%',
    'solvedate' => '8%',
    'delay'     => '10%'
];

$tbl_header = '
<table border="1" cellpadding="4" style="border-collapse:collapse; width:100%; font-size:7px;">
    <thead>
        <tr style="background-color:#334155; color:#ffffff; font-weight:bold;">
            <th width="'.$widths['id'].'" align="center">ID</th>
            <th width="'.$widths['entity'].'">Entity</th>
            <th width="'.$widths['date'].'" align="center">Opening Date</th>
            <th width="'.$widths['title'].'">Title</th>
            <th width="'.$widths['status'].'" align="center">Status</th>
            <th width="'.$widths['sla'].'" align="center">SLA / Violation</th>
            <th width="'.$widths['pending'].'" align="center">Pending (Time/Reason)</th>
            <th width="'.$widths['audit'].'" align="center">Audit</th>
            <th width="'.$widths['deadlines'].'" align="center">Deadlines</th>
            <th width="'.$widths['solvedate'].'" align="center">Solved</th>
            <th width="'.$widths['delay'].'" align="center">Delay (TTO/TTR)</th>
        </tr>
    </thead>
    <tbody>';

$tbl_rows = '';
foreach ($tickets as $t) {
    $bg = ($t['status'] == 'violated') ? '#fef2f2' : '#ffffff';
    $status_col = ($t['status'] == 'violated') ? '#ef4444' : (($t['status'] == 'active') ? '#3b82f6' : '#10b981');
    
    $audit_text = strtoupper($t['audit']['risk_level']);
    $audit_col = ($t['audit']['risk_level'] == 'high' ? '#ef4444' : ($t['audit']['risk_level'] == 'suspicious' ? '#f59e0b' : '#10b981'));
    $flags_text = implode(', ', $t['audit']['flags']);

    $sla_info = ($t['sla_name'] ?: '-') . '<br><small>(' . ($t['violation_type'] ?: 'None') . ')</small>';
    $pending_info = '<b>' . $t['pending_formatted'] . '</b><br><small>' . htmlspecialchars($t['pending_reason']) . '</small>';

    $tbl_rows .= '<tr style="background-color:'.$bg.';">
        <td width="'.$widths['id'].'" align="center">#'.$t['id'].'</td>
        <td width="'.$widths['entity'].'">'.htmlspecialchars(mb_strimwidth($t['entity'], 0, 20, "...")).'</td>
        <td width="'.$widths['date'].'" align="center">'.$t['date'].'</td>
        <td width="'.$widths['title'].'">'.htmlspecialchars(mb_strimwidth($t['name'], 0, 30, "...")).'</td>
        <td width="'.$widths['status'].'" align="center" style="color:'.$status_col.'; font-weight:bold;">'.$t['status_label'].'</td>
        <td width="'.$widths['sla'].'" align="center" style="font-size: 6px;">'.$sla_info.'</td>
        <td width="'.$widths['pending'].'" align="center" style="font-size: 6px;">'.$pending_info.'</td>
        <td width="'.$widths['audit'].'" align="center" style="color:'.$audit_col.'; font-size: 6px;"><b>'.$audit_text.'</b><br>'.htmlspecialchars($flags_text).'</td>
        <td width="'.$widths['deadlines'].'" align="center" style="font-size: 6px;">TTO: '.($t['tto_deadline'] ? Html::convDateTime($t['tto_deadline']) : '-').'<br>TTR: '.($t['ttr_deadline'] ? Html::convDateTime($t['ttr_deadline']) : '-').'</td>
        <td width="'.$widths['solvedate'].'" align="center">'.($t['solvedate'] ? Html::convDateTime($t['solvedate']) : '-').'</td>
        <td width="'.$widths['delay'].'" align="right" style="font-size: 6px;">'.($t['tto_delay_formatted'] ?: '-').' / '.($t['solve_delay_formatted'] ?: '-').'</td>
    </tr>';
}

$tbl_footer = '</tbody></table>';

$pdf->writeHTML($tbl_header . $tbl_rows . $tbl_footer, true, false, false, false, '');

// --- LEGEND / FOOTNOTE ---
$pdf->Ln(5);
$pdf->SetFont('dejavusans', '', 7);
$legend_html = '
<table cellpadding="4" style="background-color:#f1f5f9; border: 1px solid #cbd5e1; width:100%;">
    <tr>
        <td>
            <b>SLA Audit Legend / Denetim Sözlüğü:</b><br>
            <b>HIGH RISK:</b> SLA manipülasyonu belirtileri (Yüksek Risk).<br>
            <b>SUSPICIOUS:</b> Olağandışı kullanım örüntüleri (Şüpheli).<br>
            <b>NORMAL:</b> Kurallara uygun yönetim.
        </td>
        <td>
            <b>Risk Flags / Risk Bayrakları:</b><br>
            <b>stagnant:</b> Bekleme süresi SLA süresini aşmış (Durağan).<br>
            <b>last_minute:</b> SLA bitimine %10 kala beklemeye alınmış (Son Dakika).<br>
            <b>excessive_toggling:</b> 3 kereden fazla beklemeye al/çıkar yapılmış (Aşırı Git-Gel).
        </td>
    </tr>
</table>';
$pdf->writeHTML($legend_html, true, false, false, false, '');

$pdf->Output('SLA_Report_'.date('Ymd').'.pdf', 'I');
