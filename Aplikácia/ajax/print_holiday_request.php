<?php
setlocale(LC_CTYPE, "en_US.UTF-8");
putenv("LC_CTYPE=en_US.UTF-8");

require '../include/config.php';
require '../class/user.php';
require '../class/day.php';
require '../template/calendar.php';

function tex_safe_chars_only($string, $replacement = ' ') {
    return preg_replace('/[^.,:;!?(\[\])[:alnum:][:space:]—–-]/u', $replacement, $string);
}

// kontrola statusu prihláseného používateľa
$my_account = User::login(User::STATUS_REGULAR);
$personal_id = intval($my_account->personal_id);
$user = $my_account;

if ( post(["personal_id"]) &&
    $my_account->secretary &&
    intval(post("personal_id")) > 0 ) {
  $personal_id = intval( post("personal_id") );
  $user = User::get( $personal_id );
}

$data = array(
    "meno" => $user->name,
    "priezvisko" => $user->surname,
    "osobnecislo" => $personal_id,
    "utvar" => $department,
    "cisloutvaru" => $department_id,
    "rok" => post("year"),
    "dovolenkaod" => post("from_time"),
    "dovolenkado" => post("to_time"),
    "dovolenkadni" => post("num_of_days"),
    "datum" => post("request_date")
);

$texcmds = array_map(function ($key, $value) {
        return "\\newcommand\\$key{" . tex_safe_chars_only($value) . "}\n";
    },
    array_keys($data), $data);

$jobname = preg_replace('/[^a-zA-Z0-9]/u', '-', $user->username);
list($tmpdir, $etc) = exec_or_die(
    "mktemp",
    ["--directory", "--tmpdir", "pritomnost.$jobname.XXXXXXXXXX"]
);

file_put_contents("$tmpdir/data.tex", $texcmds);

$printer_option_args = [];
foreach ($printer_options as $opt) {
    $printer_option_args[] = '-o';
    $printer_option_args[] = $opt;
}

list($lastout, $etc) = exec_or_die(
    "../tools/dovolenkovy-listok.sh",
    array_merge(
        [$tmpdir, $jobname, $printer_host, $printer],
        $printer_option_args
    )
);

set_plain_output();
echo htmlspecialchars($lastout);
