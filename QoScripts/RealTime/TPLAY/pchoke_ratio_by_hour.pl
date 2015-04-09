#! /usr/bin/env perl

use Time::Local;

$date = shift @ARGV;
$key = shift @ARGV; #hour
$playtype = shift @ARGV;
$savedir = shift @ARGV;
$filename = shift @ARGV;

open FILE, "<$filename";
while(<FILE>) {
	chomp;
	@element = split /\|/;

	if ($element[34] != $playtype) {
		next;
	}
	
	#print "$key\n";
	if ($element[31] == 1) {
		
		$year = substr($element[11], 0, 4);
		$month = substr($element[11], 4, 2)-1;
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
		$month = substr($element[12], 4, 2)-1;
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
	    if($watch_time<0 || $watch_time>36000) {
			next;
		}
	
		if ($element[17] == 0) {
			$suc{$key} += 1;
		}
		else {
			$fail{$key} += 1;
			
			$pchoke_play_time{$key} += $watch_time;
			$pchoke_time{$key} += $element[16];
			
			$pnum{$key} .= $element[17]." ";
		}
		
		$watch{$key} .= $watch_time." ";
		
		$play_time{$key} += $watch_time;		
	}
}
close FILE;
	
# for write results
$k = $key;

$sum = 0;
$tw = 0;

$total = $suc{$k}+$fail{$k};
$ratio = ($total==0) ? 0 : $suc{$k}/($suc{$k}+$fail{$k});
$pchoke_time_rate = $pchoke_play_time{$k}==0 ? 0 : $pchoke_time{$k}/$pchoke_play_time{$k};
$all_pchoke_time_rate = $play_time{$k}==0 ? 0 : $pchoke_time{$k}/$play_time{$k};
	
@ptime = split / /, $watch{$k};

@time_sorted = sort { $a <=> $b } @ptime;
$suc_total = @time_sorted;
$idx_25 = $suc_total * 0.25;
$idx_50 = $suc_total * 0.50;
$idx_75 = $suc_total * 0.75;
$idx_90 = $suc_total * 0.90;
$idx_95 = $suc_total * 0.95;
		
@pn = split / /, $pnum{$k};
$sum += $_ for @pn;
$avg = ($fail{$k}==0)?0:$sum/$fail{$k};
		
$tw += $_ for @ptime;
$avgw = ($total==0)?0:$tw/$total;
	
open OUT, ">>$savedir/pchoke_by_hour_$playtype";
printf OUT ("|%s|%.3f|%.3f|%.3f|%.2f|%d|%d|%d|%d|%d|%.2f|%d|\n", $k, $pchoke_time_rate, $all_pchoke_time_rate, $ratio, $avg, $time_sorted[$idx_25], $time_sorted[$idx_50], $time_sorted[$idx_75], $time_sorted[$idx_90], $time_sorted[$idx_95], $avgw, $suc{$k}+$fail{$k});
close OUT;

