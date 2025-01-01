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
    "absences" => Overview::get_absences_gastro($year, $month)
];

$jsonData = json_encode($report_data);

$tempInput = tempnam(sys_get_temp_dir(), 'gastro_input_');
$tempOutput = tempnam(sys_get_temp_dir(), 'gastro_output_');

file_put_contents($tempInput, $jsonData);

$outfname = preg_replace('/[^a-zA-Z0-9.]/', '-',
    sprintf("gastro-%02d/%02d.xlsx", $month, $year % 100)
);

$descriptorSpec = [
    0 => ['file', $tempInput, 'r'],  // stdin
    2 => ['pipe', 'w']               // stderr
];

$process = proc_open(["./gastro-report.py", $tempOutput], $descriptorSpec, $pipes);

if (is_resource($process)) {
    while (!feof($pipes[2])) {
        $errorOutput = fgets($pipes[2]);
        if ($errorOutput) {
            error_log("Python script error: " . $errorOutput);
        }
    }
    fclose($pipes[2]);
    
    header("Content-Description: Vykaz stravneho za $year-$month");
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename="'.$outfname.'"');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    
    readfile($tempOutput);
    
    unlink($tempInput);
    unlink($tempOutput);
    proc_close($process);
} else {
    header('HTTP/1.1 500 Internal Server Error');
    exit("Nepodarilo sa spustiť Python skript");
}
?>
