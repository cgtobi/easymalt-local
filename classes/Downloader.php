<?php

namespace PPLocalFinances;

define('OPT_ESCAPE_ARGS', 1);
define('OPT_URL_ENCODE', 2);

class Downloader
{
    public static function downloadTangerine($config_file) {
        static::_log(LOG_LEVEL_INFO, "[D] Downloading 'Tangerine' transactions ...");

        $ofxclient = Config::get('OFXCLIENT_EXECUTABLE');

        foreach (glob('data/tangerine-*') as $file) {
            unlink($file);
        }

        // Find all accounts in ofxclient.ini
        $accounts = [];
        $config_content = explode("\n", file_get_contents($config_file));
        foreach ($config_content as $line) {
            if (preg_match('/\[([0-9a-f]+)\]/', $line, $re)) {
                $accounts[] = $re[1];
            }
        }

        foreach ($accounts as $account) {
            $args = [
                '--config', escapeshellarg($config_file),
                '--account', escapeshellarg($account),
                '--download', escapeshellarg("data/tangerine-$account.ofx")
            ];
            static::_exec($ofxclient, $args);
        }
    }

    public static function downloadBNC($username, $password, $security_questions) {
        // Arguments: username, password, question1, answer1[, question2, answer2[, ...]]
        $args = [$username, $password];
        foreach ($security_questions as $q => $a) {
            $args[] = $q;
            $args[] = $a;
        }
        static::_download("Banque Nationale du Canada", 'bnc-ca', 'download/bnc-ca.sh', $args, OPT_ESCAPE_ARGS|OPT_URL_ENCODE);
    }

    public static function downloadPCFinance($username, $password, $answer, $language) {
        $args = [
            $username,
            $password,
            $answer,
            $language
        ];
        static::_download("PC Finance Mastercard", 'pc-fin', 'download/cc-generic.sh pc-fin', $args, OPT_ESCAPE_ARGS|OPT_URL_ENCODE);
    }

    public static function downloadChaseCanada($username, $password, $answer, $language) {
        $args = [
            $username,
            $password,
            $answer,
            $language
        ];
        static::_download("Chase Canada VISA", 'chase-can', 'download/cc-generic.sh chase-can', $args, OPT_ESCAPE_ARGS|OPT_URL_ENCODE);
    }

    private static function _download($bank_name, $bank_code, $command, $args, $options = 0) {
        static::_log(LOG_LEVEL_INFO, "[D] Downloading '$bank_name' transactions ...");
        foreach (glob("data/$bank_code-*") as $file) {
            unlink($file);
        }
        static::_exec($command, $args, $options);
    }

    private static function _exec($command, $arguments, $options=0) {
        if (($options & OPT_URL_ENCODE) === OPT_URL_ENCODE) {
            $arguments = array_map(
                function ($el) {
                    return urlencode($el);
                },
                $arguments
            );
        }
        if (($options & OPT_ESCAPE_ARGS) === OPT_ESCAPE_ARGS) {
            $arguments = array_map(
                function ($el) {
                    return escapeshellarg($el);
                },
                $arguments
            );
        }
        $arguments = implode(' ', $arguments);
        $command = "$command $arguments";
        static::_log(LOG_LEVEL_DEBUG, "[D] $command");
        exec("$command 2>&1", $output, $return_value);
        if ($return_value !== 0) {
            static::_log(LOG_LEVEL_WARNING, "  Warning: " . implode("\n", $output));
        }
    }

    private static function _log($log_level, $log) {
        if ($log_level > Config::get('LOG_LEVEL')) {
            return;
        }
        echo "$log\n";
    }
}
