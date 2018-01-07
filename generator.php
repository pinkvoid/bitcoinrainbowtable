<?php

$dbhost = "localhost";
$dbname = "brt";
$dbusername = "brt";
$dbpassword = "brt";

$link = new PDO("mysql:host=$dbhost;dbname=$dbname", $dbusername, $dbpassword);

$statement = $link->prepare("INSERT INTO brt(address, pkey)
	    VALUES(:address, :pkey)");

$limit = 1000;// adapt for your performance

#for($i=0; $i<$limit; $i++){
$buffer = [];
while(true){
	$_new=array_filter(explode("\n",str_replace('|',"\n",`python test.py`)));
	print_r($_new);
	foreach($_new as $new){
		$pair = explode(',', $new);
		$buffer[] = '(\''.trim($pair[1]).'\',\''.trim($pair[0]).'\')';
		if(count($buffer) == 100){
			#echo("INSERT INTO brt(address,pkey) VALUES ".implode(',',$buffer)); 
			$out=$link->query("INSERT INTO brt(address,pkey) VALUES ".implode(',',$buffer)); 
			$buffer=[];
			                if(!$out){
						                        print_r($link->errorInfo());
									                }

		}
	}
	#sleep(5);// adapt for your performance
}
