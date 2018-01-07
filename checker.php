<?php

$dbhost = "localhost";
$dbname = "brt";
$dbusername = "brt";
$dbpassword = "brt";

$link = new PDO("mysql:host=$dbhost;dbname=$dbname", $dbusername, $dbpassword);

$search = $link->prepare("SELECT address FROM richest  WHERE address=:address");
$update = $link->prepare("UPDATE brt SET verified=:timestamp WHERE address=:address");
$batch = $link->prepare("SELECT address FROM brt WHERE verified IS NULL LIMIT 100");

$done = 0;
while(true){
	$batch->execute();
	$result = $batch->fetchAll(PDO::FETCH_NUM);

	foreach($result as $_address){
		$address=$_address[0];
		$search->execute([':address' => $address]);
		$found = $search->fetch(PDO::FETCH_NUM);

		if(!empty($found)){
			print_r($found);die;
			file_put_contents(__DIR__.'/FOUND', $address);
			echo 'FOUND!!!!!!!!'."\n";
		}
		$out=$update->execute([
			    ':timestamp' => date('Y-m-d H:i:s'),
			    ':address' => $address,
		    ]);
		if(!$out){
			print_r($link->errorInfo());
		}
	}
	$done+=100;
	echo "Done: $done\n";

	sleep(3);
}
