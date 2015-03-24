#! /usr/bin/env perl

$date = shift @ARGV;
$key = shift @ARGV; #hour
$playtype = shift @ARGV;
$savedir = shift @ARGV;

$filename = shift @ARGV;

open FILE, "<$filename";
while(<FILE>) {
	chomp;
	@element = split /\|/;
	
	if ($element[34] == $playtype) {
		if ($element[31] == 1) {
			$suc{$key} += 1;
	        $suc_time{$key} .= $element[15]." ";
		}
		else {
			$fail{$key} += 1;
		}
	}
}
close FILE;

# for write results
$k = $key;

$tw = 0;

$total = $suc{$k}+$fail{$k};
$ratio = ($total == 0) ? 0 : $suc{$k}/$total;

@ptime = split / /, $suc_time{$k};

@time_sorted = sort { $a <=> $b } @ptime;
$suc_total = @time_sorted;
$idx_25 = $suc_total * 0.25;
$idx_50 = $suc_total * 0.50;
$idx_75 = $suc_total * 0.75;
$idx_90 = $suc_total * 0.90;
$idx_95 = $suc_total * 0.95;

$tw += $_ for @ptime;
$avgw = ($suc_total == 0)?0:$tw/$suc_total;

open OUT, ">>$savedir/fbuffer_data_by_hour_$playtype";
printf OUT ("|%d|%.2f|%d|%d|%d|%d|%d|%d|%d|\n", $k, $ratio, $time_sorted[$idx_25], $time_sorted[$idx_50], $time_sorted[$idx_75], $time_sorted[$idx_90], $time_sorted[$idx_95], $avgw, $total);
close OUT;

delete @suc{keys %suc};
delete @fail{keys %fail};
delete @suc_time{keys %suc_time};
