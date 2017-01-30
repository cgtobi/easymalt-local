<?php

namespace PPLocalFinances;

class Importer
{
    public static function importTangerine() {
        $ofxParser = new \OfxParser\Parser();
        $data_files_dir = 'data';
        $data_files_prefix = 'tangerine-';
        $files_glob = $data_files_dir . DIRECTORY_SEPARATOR . $data_files_prefix . '*.ofx';
        foreach (glob($files_glob) as $file) {
            $ofx = $ofxParser->loadFromFile($file);
            $bankAccount = array_shift($ofx->bankAccounts);

            $q = "SELECT * FROM accounts WHERE routing_number = :routing_number AND account_number = :account_number";
            $account = DB::getFirst($q, ['routing_number' => (string) $bankAccount->routingNumber, 'account_number' => (string) $bankAccount->accountNumber]);
            $account_id = (int) $account->id;

            static::_log(LOG_LEVEL_INFO, "[I] " . $account->name);

            $q = "INSERT INTO accounts 
                     SET routing_number = :routing_number, account_number = :account_number, balance = :balance, currency = :currency, balance_date = :balance_date 
                      ON DUPLICATE KEY UPDATE balance = VALUES(balance), balance_date = VALUES(balance_date)";
            DB::insert(
                $q,
                [
                    'routing_number' => (string) $bankAccount->routingNumber,
                    'account_number' => (string) $bankAccount->accountNumber,
                    'currency' => (string) $bankAccount->statement->currency,
                    'balance' => (float) $bankAccount->balance,
                    'balance_date' => date('Y-m-d H:i:s', $bankAccount->balanceDate->getTimestamp())
                ]
            );

            $transactions = $bankAccount->statement->transactions;
            foreach ($transactions as $t) {
                static::_addTransaction($account_id, $t);
            }
        }
    }

    public static function importBNC() {
        $ofxParser = new \OfxParser\Parser();
        $data_files_dir = 'data';
        $data_files_prefix = 'bnc-ca-';
        $files_glob = $data_files_dir . DIRECTORY_SEPARATOR . $data_files_prefix . '*.ofx';
        foreach (glob($files_glob) as $file) {
            $ofx = $ofxParser->loadFromFile($file);
            $bankAccount = array_shift($ofx->bankAccounts);

            $q = "SELECT * FROM accounts WHERE routing_number = :routing_number AND account_number = :account_number";
            $account = DB::getFirst($q, ['routing_number' => '11011', 'account_number' => (string) $bankAccount->accountNumber]);
            $account_id = (int) $account->id;

            static::_log(LOG_LEVEL_INFO, "[I] " . $account->name);

            $q = "INSERT INTO accounts 
                     SET routing_number = :routing_number, account_number = :account_number, balance = :balance, currency = :currency, balance_date = :balance_date 
                      ON DUPLICATE KEY UPDATE balance = VALUES(balance), balance_date = VALUES(balance_date)";
            DB::insert(
                $q,
                [
                    'routing_number' => '11011',
                    'account_number' => (string) $bankAccount->accountNumber,
                    'currency' => (string) $bankAccount->statement->currency,
                    'balance' => (float) $bankAccount->balance,
                    'balance_date' => date('Y-m-d H:i:s', $bankAccount->balanceDate->getTimestamp())
                ]
            );

            $transactions = $bankAccount->statement->transactions;
            foreach ($transactions as $t) {
                static::_addTransaction($account_id, $t);
            }
        }
    }

    public static function importPCFinance() {
        static::_importGenericCC('pc-fin', '5228790001480970');
    }

    public static function importChaseCanada() {
        static::_importGenericCC('chase-can', '4685631474986490');
    }

    public static function postProcess() {
        static::_log(LOG_LEVEL_INFO, "[PP] Post-processing transactions ... ");
        $q = "SELECT * FROM post_processing ORDER BY prio DESC";
        $pp_settings = DB::getAll($q);

        $q = "SELECT * FROM transactions WHERE post_processed = 'no' ORDER BY id";
        $transactions = DB::getAll($q);
        foreach ($transactions as $t) {
            foreach ($pp_settings as $pp) {
                if (preg_match('@' . $pp->regex . '@i', $t->name . ' ' . $t->memo, $re)) {
                    $params = ['txn_id' => (int) $t->id];
                    $updates = [];
                    $log_details = [];
                    if (!empty($pp->display_name)) {
                        $updates[] = 'display_name = :display_name';
                        $display_name = $pp->display_name;
                        for ($i=1; $i<count($re); $i++) {
                            $display_name = str_replace('{'.$i.'}', $re[$i], $display_name);
                        }
                        $params['display_name'] = $display_name;
                        $log_details[] = "Name: $display_name";
                    }
                    if (!empty($pp->category)) {
                        $updates[] = 'category = :category';
                        $params['category'] = $pp->category;
                        $log_details[] = "Category: $pp->category";
                    }
                    if (!empty($pp->tags)) {
                        $updates[] = 'tags = :tags';
                        $params['tags'] = $pp->tags;
                        $log_details[] = "Tags: $pp->tags";
                    }
                    if (!empty($updates)) {
                        static::_log(LOG_LEVEL_INFO, "  $t->name => " . implode("  ", $log_details));
                        $updates[] = "post_processed = 'yes'";
                        $q = "UPDATE transactions SET " . implode(", ", $updates) . " WHERE id = :txn_id";
                        DB::execute($q, $params);
                        break;
                    }
                }
            }
        }
    }

    private static function _importGenericCC($bank_code, $account_number) {
        $data_files_dir = 'data';
        $data_files_prefix = "$bank_code-";

        $q = "SELECT * FROM accounts WHERE account_number = :number";
        $account = DB::getFirst($q, $account_number);
        $account_id = (int) $account->id;

        static::_log(LOG_LEVEL_INFO, "[I] " . $account->name);

        // Balance
        $file = $data_files_dir . DIRECTORY_SEPARATOR . $data_files_prefix . 'balance.txt';
        if (file_exists($file)) {
            $date = date('Y-m-d H:i:s', filemtime($file));
            $amount = trim(file_get_contents($file));
            $negative = ($amount[0] === '(');
            if (preg_match('/(\d+),(\d\d)/', $amount, $re) || preg_match('/(\d+)\.(\d\d)/', $amount, $re)) {
                $amount = -($re[1] + ($re[2]/100));
                if ($negative) {
                    $amount *= -1;
                }
                $q = "UPDATE accounts SET balance = :balance, balance_date = :date WHERE id = :account_id";
                DB::execute($q, ['account_id' => $account_id, 'balance' => $amount, 'date' => $date]);
            } else {
                static::_log(LOG_LEVEL_ERROR, "  Error: unparseable amount: $amount");
            }
        }

        // Transactions
        $files_glob = $data_files_dir . DIRECTORY_SEPARATOR . $data_files_prefix . '*.tsv';
        foreach (array_reverse(glob($files_glob)) as $file) {
            $tsv = mb_convert_encoding(file_get_contents($file), 'utf-8', 'iso-8859-1');
            $first_line = TRUE;
            foreach (explode("\n", $tsv) as $line) {
                if ($first_line) {
                    $first_line = FALSE;
                    continue;
                }
                if (empty($line)) {
                    continue;
                }
                $line = explode("\t", $line);

                $amount = trim($line[2], '" ');
                $negative = ($amount[0] === '(');
                if (preg_match('/(\d+),(\d\d) \$/', $amount, $re)) {
                    $line_lang = 'fr';
                    $amount = -($re[1] + ($re[2]/100));
                } elseif (preg_match('/\$(\d+).(\d\d)/', $amount, $re)) {
                    $line_lang = 'en';
                    $amount = -($re[1] + ($re[2]/100));
                } else {
                    static::_log(LOG_LEVEL_ERROR, "  Error: unparseable amount: $line[2]");
                    continue;
                }
                if ($negative) {
                    $amount *= -1;
                }

                if (preg_match('@(\d+)/(\d+)/(\d+)@', $line[0], $re)) {
                    if ($line_lang == 'fr') {
                        $date = $re[3] . "-" . $re[2] . "-" . $re[1];
                    } else {
                        $date = $re[3] . "-" . $re[1] . "-" . $re[2];
                    }
                } else {
                    static::_log(LOG_LEVEL_ERROR, "  Error: unparseable date found: $line[0]");
                    continue;
                }

                $line[8] = trim($line[8]);
                if ($line[8] == 'C') {
                    $type = 'CREDIT';
                } elseif ($line[8] == 'D') {
                    $type = 'DEBIT';
                } else {
                    static::_log(LOG_LEVEL_ERROR, "  Error: unknown type found: $line[8]");
                    continue;
                }

                $t = (object) [
                    'date' => new \DateTime($date),
                    'amount' => $amount,
                    'type' => $type,
                    'uniqueId' => trim($line[7], '" '),
                    'name' => trim($line[3], '" '),
                    'memo' => trim($line[4], '" ') . " " . $line[5] . " " . $line[6],
                ];

                static::_addTransaction($account_id, $t);
            }
        }
    }

    private static function _addTransaction($account_id, $t) {
        $date_time = date('Y-m-d H:i:s', $t->date->getTimestamp());
        $date = substr($date_time, 0, 10);

        $q = "SELECT 1 FROM transactions WHERE account_id = :account_id AND unique_id = :unique_id";
        $txn_exists = DB::getFirstValue($q, ['account_id' => $account_id, 'unique_id' => (string) $t->uniqueId]);

        $log_level = ($txn_exists ? LOG_LEVEL_DEBUG : LOG_LEVEL_INFO);
        static::_log($log_level, "  [T] $date  " . sprintf("%10s", number_format($t->amount, 2)) . "  $t->name");
        $q = "INSERT IGNORE INTO transactions
                 SET account_id = :account_id, unique_id = :unique_id, `date` = :date, `type` = :type, amount = :amount, name = :name, memo = :memo";
        DB::insert(
            $q,
            [
                'account_id' => $account_id,
                'unique_id' => (string) $t->uniqueId,
                'date' => $date_time,
                'type' => (string) $t->type,
                'amount' => $t->amount,
                'name' => (string) $t->name,
                'memo' => (string) $t->memo
            ]
        );
    }

    private static function _log($log_level, $log) {
        if ($log_level > Config::get('LOG_LEVEL')) {
            return;
        }
        echo "$log\n";
    }
}
