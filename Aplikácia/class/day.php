<?php

class Day {
  var $year = 0;
  var $month = 0;
  var $day = 0;

  var $absence_id = 0;
  var $date = "";
  var $day_of_week = 0;
  var $user_id = 0;
  var $holiday = "";
  var $type = 0;
  var $description = "";
  var $public = 1;
  var $confirmation = 0;
  var $from_time = "08:00:00";
  var $to_time = "16:00:00";
  var $insert_time = "";

  // zostav den podla user_id a datumu
  function __construct( $d, $m, $y, $user_id ) {
    global $conn;

    $this->date = date("Y-m-d", strtotime( intval($y)."-".intval($m)."-".intval($d) ) );
    $this->year = intval($y);
    $this->month = intval($m);
    $this->day = intval($d);

    $this->day_of_week = date("N", strtotime( $this->date ) );
    $this->user_id = intval($user_id);

    $holiday = $conn->query( "SELECT description FROM holidays WHERE date_time = '$this->date'" );
    if ( $holiday = $holiday->fetch_assoc() ) $this->holiday = $holiday["description"];

    $day = $conn->query( "SELECT * FROM absence WHERE user_id = '$this->user_id' AND date_time = '$this->date'" );

    if ( $day = $day->fetch_assoc() ) {
      $this->absence_id = $day['id'];
      $this->type = $day['type'];
      $this->description = $day['description'];
      $this->public = $day['public'];
      $this->confirmation = $day['confirmation'];
      $this->from_time = $day['from_time'];
      $this->to_time = $day['to_time'];
      $this->insert_time = $day['insert_time'];
    }
  }

  // getni den podla id
  static function get( $_id ) {
    global $conn;

    $id = intval( $_id );
    $a = $conn->query("SELECT DAY(date_time) as d, MONTH(date_time) as m, YEAR(date_time) as y, user_id
                          FROM absence WHERE id = '$id'");
    if ( $a = $a->fetch_assoc() )
      return new Day( $a["d"], $a["m"], $a["y"], $a["user_id"] );
    else
      return false;
  }

  function set( $_type, $_public, $_description, $_from_time, $_to_time ) {
    global $sk_types, $sk_subtypes, $my_account;

    $type = intval( $_type );
    $public = intval( boolval($_public) );
    $description = $_description;

    $from_time = date("H:i:s", strtotime("$this->date $_from_time"));
    $to_time = date("H:i:s", strtotime("$this->date $_to_time"));

    if ( $this->type || $this->holiday ) return false;
    if ( strtotime("$this->date $from_time") > strtotime("$this->date $to_time") ) return false;
    if ( $type <= 0 || $type > sizeof($sk_types) ) return false;
    if ( !edit_date( $this->year, $this->month, $type ) && !$my_account->secretary ) return false;

    $this->confirmation = 1;
    if ( $type == ABSENCE_TRAVEL || $type == ABSENCE_WORKFROMHOME ) $this->confirmation = 0;

    $this->type = $type;
    $this->public = $public;
    $this->description = $description;
    $this->from_time = $from_time;
    $this->to_time = $to_time;

    return true;
  }

  static function header_encode($content) {
    return '=?UTF-8?B?' . base64_encode($content) . '?=';
  }

  function insert() {
    global $conn, $request_validators, $sk_types, $main_url, $sending_mails;

    $sql = $conn->prepare("INSERT INTO absence (user_id, date_time, from_time, to_time, description, type, insert_time, public, confirmation)
    VALUES ('$this->user_id', '$this->date', '$this->from_time', '$this->to_time', ?, '$this->type', NOW(), '$this->public', '$this->confirmation')" );
    $sql->bind_param('s', $this->description);

    if ( $this->type != ABSENCE_WORKFROMHOME && $this->type != ABSENCE_TRAVEL ) return $sql->execute();

    if ( $sql->execute() ) {
      if ( $sending_mails ) {
        $validator = User::get($request_validators[0]);
        $requestor = User::get_by_id($this->user_id);

	$email = $validator->email;
        $headers  = 'MIME-Version: 1.0' . "\r\n";
        $headers .= 'Content-type: text/html; charset=UTF-8' . "\r\n";
        $headers .= 'From: ' . Day::header_encode('Prítomnosť') . ' <noreply@pritomnost.dai.fmph.uniba.sk>' . "\r\n";
	$subject = "Žiadosť o schválenie neprítomnosti (" . sk_format_date($this->date) . ")";
        $text = "<p>Nová žiadosť na schválenie.</p>\r\n" .
            "<dl>\r\n" .
            "<dt>Žiadateľ*ka:</dt> <dd>" . $requestor->name . " " . $requestor->surname . "</dd>\r\n" .
            "<dt>Typ neprítomnosti:</dt> <dd>" . $sk_types[$this->type] . " </dd>\r\n" .
            "<dt>Dátum: </dt> <dd>" . sk_format_date($this->date) . "</dd>\r\n" .
            "</dl>\r\n" .
            "<p>Pre schválenie pokračujte na adresu: <a href='$main_url/requests.php'>$main_url/requests.php</a></p>";
        mail($email, Day::header_encode($subject), $text, $headers);
      }
      return true;
    }
    else
      return false;
  }

  function remove() {
    global $conn;

    if ( !$this->absence_id ) return false;
    $result = $conn->query( "DELETE FROM absence WHERE id = '$this->absence_id'" );
    return ($result === TRUE);
  }
}

?>
