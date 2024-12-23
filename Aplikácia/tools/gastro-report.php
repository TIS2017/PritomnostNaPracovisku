<?php

require_once '../include/config.php';
require_once '../include/db_utils.php';
require_once '../class/user.php';
require_once '../class/overview.php';

// kontrola statusu prihlaseneho pouzivatela
$my_account = User::login(User::STATUS_SECRETARY);

// nastav rok a mesiac ( ak su neplatne nastavi aktualny rok a mesiac )
$year = get_year();
$month = get_month();

$report_data = [
    "year" => $year,
    "month" => $month,
    "month_sk" => $sk_months[$month],
    "personal_id_prefix" => $personal_id_prefix,
    "employees" => User::get_users(),
    "public_holidays" => Overview::get_public_holidays($year, $month),
    "absences" => Overview::get_absences_gastro($year, $month),
    "holidays_budget" => Overview::get_holidays_budget($year, $month)
];

$jsonData = json_encode($report_data);

$inputStream = fopen('php://memory', 'r+');
fwrite($inputStream, $jsonData);
rewind($inputStream);

$outputStream = fopen('php://temp', 'r+');

$outfname = preg_replace('/[^a-zA-Z0-9.]/', '-',
    sprintf("%02d-gastro-%02d.xlsx", $month, $year % 100)
);

$descriptorSpec = [
    0 => $inputStream,     // stdin
    1 => $outputStream,    // stdout
    2 => ['pipe', 'w']     // stderr
];

$process = proc_open("./gastro_report.py", $descriptorSpec, $pipes);

if (is_resource($process)) {
    fclose($pipes[2]);
    
    header("Content-Description: Vykaz stravneho za $year-$month");
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename="'.$outfname.'"');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    
    rewind($outputStream);
    fpassthru($outputStream);
    
    fclose($inputStream);
    fclose($outputStream);
    
    proc_close($process);
} else {
    header('HTTP/1.1 500 Internal Server Error');
    exit("Nepodarilo sa spustiť Python skript");
}
?>
