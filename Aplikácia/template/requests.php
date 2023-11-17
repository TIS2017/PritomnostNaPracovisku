<?php

function print_requests( $year, $year_minus, $year_plus, $str, $all_months ){
  return "
  <div class='content' id='requests'>
    <div class='title_1'>Žiadosti
      <div class='subtitle'>
          <a href='requests.php?year=$year_minus&all_months=$all_months' title='$year_minus'><span class='fa fa-chevron-circle-left'></span></a>
          $year&nbsp;&nbsp;&nbsp;
          <a href='requests.php?year=$year_plus&all_months=$all_months' title='$year_plus'><span class='fa fa-chevron-circle-right'></span></a>
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; [" . (($all_months==1)?'všetky':'iba posledné') . "] <a href='requests.php?year=$year&all_months=" . (($all_months==1)?0:1) . "'>prepnúť</a>
      </div>
    </div>

    <div id='info_container'></div>

    <div class='table_3'>
      <table>
        <tr>
          <th>Dátum</th>
          <th>Popis</th>
          <th>Schválenie</th>
        </tr>
        $str
      </table>
    </div>

  </div>
  ";
}

function print_requests_table_row ( $id, $date, $time, $user_name, $type, $description, $confirmed ) {
  if ( $confirmed ) {
    $class = 'enable';
    $confstr = 'Schválená';
  } else {
    $class = 'disable';
    $confstr = 'Schváliť';
  }
  return "
  <tr id='request_$id'>
    <td>$date <div>$time</div></td>
    <td>$user_name &ndash; $type<br><span class='desc'>$description</span></td>
    <td onclick='request_set($id);' id='request_check_$id' class='$class' title='$confstr'><span class='fa fa-check'></span></td>
  </tr>
  ";
}

function print_terms_table_row_empty() {
  return "<tr><td colspan='3'>Žiadne záznamy...</td></tr>";
}

?>
