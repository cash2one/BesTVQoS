#! /usr/bin/env perl

use Time::Local;

$date = shift @ARGV;
$savedir = shift @ARGV;
$filename = shift @ARGV;

open FILE, "<$filename";
while(<FILE>) {
	chomp;
	@element = split /\|/;
	
	if ($element[31] == 1) {
		
		$year = substr($element[11], 0, 4);
		$month = substr($element[11], 4, 2);
		$day = substr($element[11], 6, 2);
		$hour = substr($element[11], 8, 2);
		$min = substr($element[11], 10, 2);
		$sec = substr($element[11], 12, 2);
		eval{
			$beginTime = timelocal($sec, $min, $hour, $day, $month, $year);
		};
		if($@){
			next;
		}

		$year = substr($element[12], 0, 4);
		$month = substr($element[12], 4, 2);
		$day = substr($element[12], 6, 2);
		$hour = substr($element[12], 8, 2);
		$min = substr($element[12], 10, 2);
		$sec = substr($element[12], 12, 2);
		eval{
			$endTime = timelocal($sec, $min, $hour, $day, $month, $year);
		};
		if($@){
			next;
		}

		$watch_time = $endTime - $beginTime;
		if($watch_time<0 || $watch_time>36000){
            next;
        }
		
		if ($element[17] > 0) {		
			$pchoke_play_time += $watch_time;
			$pchoke_time += $element[16];
			
			$total_pnum += $element[17];
		}
	}
}
close FILE;
	
# for write results
$play_hour = $pchoke_play_time/3600;
$avgc = ($play_hour == 0) ? 0 : $total_pnum/$play_hour;
$avgt = ($play_hour == 0) ? 0 : $pchoke_time/$play_hour;

print $pchoke_time."\n";

open OUT, ">$savedir/BesTV_avg_pchoke_data";
printf OUT ("|%s|%.2f|%.2f|%.2f|\n", $date, $avgc, $avgt, $play_hour);
close OUT;

