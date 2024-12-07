<?php

function print_index_person ( $id, $name, $surname, $personal_id, $employee_type ) {
  return "
  <div class='value person' id='person_$id' data-type='{$employee_type}' onclick='overview_set_user($id);'>
    $surname $name <span class='personal_id'>$personal_id</span>
  </div>
  ";
}

function print_index( $persons, $y, $m ) {
  global $deadline, $my_account;

  $deadline_notice = $my_account->user
    ? message( "info", "<b>Dovolenku a práceneschopnosť za tento mesiac
      môžete pridávať a&nbsp;editovať do $deadline. dňa.</b><br>
      Po tomto dni sa obráťte na pani sekretárku.
      Neprítomnosť z&nbsp;ostatných dôvodov je možné zadávať do konca
      mesiaca." )
    : "";

    $filter_html = '
    <select id="employee_filter" onchange="filter_employees()">
      <option value="all">Všetci</option>
      <option value="employee">Zamestnanci</option>
      <option value="phd">Doktorandi</option>
    </select>
    ';

  return "
  <div class='content' id='overview'>
    $deadline_notice
    <div class='side_table'>
      <div class='title'>Prehľad zamestnancov $filter_html</div>
      $persons
    </div>

    <div id='overview_table'></div>
    <script>slide_overview($y, $m);</script>

    <div class='spacer'></div>
  </div>
  ";

}

?>
