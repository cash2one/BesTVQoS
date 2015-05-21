#! /usr/bin/env perl

$date = shift @ARGV;
$hour = shift @ARGV;
$idx = shift @ARGV;
$savedir = shift @ARGV;

$filename = shift @ARGV;

open FILE, "<$filename";
while(<FILE>) {
	chomp;
	@element = split /\|/;
	
	@sub = split /\?/, $element[6];
	$key = $sub[0];

	$count = @element;
    $code_idx = $count-2;
	
	if ($element[$code_idx] eq "200") {
		$suc{$key} += 1;
        $suc_time{$key} .= $element[$idx]." ";
	}
	else {
		$fail{$key} += 1;
	}

	$record{$key} += 1;
}
close FILE;

# for write results
foreach $k (sort {$record{$b}<=>$record{$a}} %suc) {
	$tw = 0;
	
	$total = $suc{$k}+$fail{$k};
	
	if($total <= 0) {
		next;
	}

	$ratio = $suc{$k}/$total;
	
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
	
	open OUT, ">>$savedir/response_data_CDF_by_url_${idx}_${hour}";
	printf OUT ("|%s|%.2f|%.2f|%.3f|%.3f|%.3f|%.3f|%.3f|%d|\n", $k, $ratio, $time_sorted[$idx_25], $time_sorted[$idx_50], $time_sorted[$idx_75], $time_sorted[$idx_90], $time_sorted[$idx_95], $avgw, $total);
	close OUT;
}
	
delete @suc{keys %suc};
delete @fail{keys %fail};
delete @suc_time{keys %suc_time};
