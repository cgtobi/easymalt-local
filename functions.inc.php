<?php

define('LOG_LEVEL_DEBUG', 7);
define('LOG_LEVEL_INFO', 6);
define('LOG_LEVEL_WARNING', 4);
define('LOG_LEVEL_ERROR', 3);
define('LOG_LEVEL_CRITICAL', 2);

function array_remove($array, $value_to_remove) {
	return array_diff($array, array($value_to_remove));
}

function he($text) {
	return htmlentities($text, ENT_COMPAT, 'UTF-8');
}

function phe($text) {
	echo he($text);
}

function js($text) {
    return str_replace("'", "\\'", $text);
}

function pjs($text) {
    echo js($text);
}

function format_phone($phone_number) {
	if (empty($phone_number)) {
		return '';
	}
	return substr($phone_number, 0, 3) . "-" . substr($phone_number, 3, 3) . "-" . substr($phone_number, 6, 4);
}

function strip_accents($text) {
	return strtr($text,'àáâãäçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ','aaaaaceeeeiiiinooooouuuuyyAAAAACEEEEIIIINOOOOOUUUUY');
}

function _array_shift($array) {
    return array_shift($array);
}

function sendPOST($url, $data, $headers=array()) {
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, TRUE);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

    $result = curl_exec($ch);

    if (!$result) {
        error_log("Error executing sendPOST$url); cURL error: " . curl_errno($ch));
    }

    curl_close($ch);

    return $result;
}

function sendGET($url, $headers=array()) {

    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

    $result = curl_exec($ch);

    if (!$result) {
        error_log("Error executing sendGET($url); cURL error: " . curl_errno($ch));
    }

    curl_close($ch);

    return $result;
}

function string_contains($haystack, $needle) {
    return strpos($haystack, $needle) !== FALSE;
}

function array_contains($haystack, $needle) {
    if (empty($haystack)) return FALSE;
    return array_search($needle, $haystack) !== FALSE;
}

// i18n

function t(/* $args... */) {
    global $I18N;
    return $I18N->translate(func_get_args());
}

function thtml(/* $args... */) {
    global $I18N;
    return $I18N->translate(func_get_args(), FALSE);
}

function ti($img_src) {
    global $I18N;
    $p = strrpos($img_src, '.');
    return substr($img_src, 0, $p) . '_' . $I18N->getLang() . substr($img_src, $p);
}

function isJSON($string){
   return is_string($string) && is_object(json_decode($string)) ? true : false;
}

function urlsafe_base64_encode($string) {
    $data = base64_encode($string);
    $data = str_replace(array('+','/','='),array('-','_',''),$data);
    return $data;
}

function urlsafe_base64_decode($string) {
    $data = str_replace(array('-','_'),array('+','/'),$string);
    $mod4 = strlen($data) % 4;
    if ($mod4) {
        $data .= substr('====', $mod4);
    }
    return base64_decode($data);
}

function reset_uploads() {
    if (isset($_SESSION['uploads'])) {
        unset($_SESSION['uploads']);
    }
}

function get_content_type($content) {

    $file_info = new finfo(FILEINFO_MIME_TYPE);
    $mime_type = $file_info->buffer($content);
    return $mime_type;
}

function get_file_extension($filename) {
    return pathinfo($filename, PATHINFO_EXTENSION);
}

function remove_file_extension($filename){
    return pathinfo($filename, PATHINFO_FILENAME);
}


/** Finances */
