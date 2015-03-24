#! /usr/bin/env perl

$date = shift @ARGV;
$playtype = shift @ARGV;

open OUT, ">$date\_$playtype\_fbuffer_data_by_hour_for_fail";

foreach $filename (@ARGV) {

	open FILE, "<$filename";
	
	$key = substr($filename, 18, 2);
	#print "$key\n";
	while(<FILE>) {
		chomp;
		@element = split /\|/;
		
		#$key = int($element[0]/3600 + 8)%24;
		#print "$element[14],";
		if ($element[34] == $playtype) {
			if ($element[31] == 0 && $element[15]<3600) {
				$suc{$key} += 1;
        $suc_time{$key} .= $element[15]." ";
        
        $suc{'24'} += 1;
        $suc_time{'24'} .= $element[15]." ";
			}
			else {
				$fail{$key} += 1;
				
				$fail{'24'} += 1;
			}
		}
	}
	
	close FILE;
	
}

@keys1 = ('00','01','02','03','04','05','06','07','08','09');
@keys2 = (10 .. 24);

foreach $k (@keys1, @keys2) {
		
		#print $k."\n";
		$tw = 0;
		
		$total = $suc{$k}+$fail{$k};
		$ratio = ($total == 0) ? 0 : $suc{$k}/$total*100;
	
		@ptime = split / /, $suc_time{$k};

  	@time_sorted = sort { $a <=> $b } @ptime;
  	$suc_total = @time_sorted;
  	$idx_25 = $suc_total * 0.25;
  	$idx_50 = $suc_total * 0.50;
  	$idx_75 = $suc_total * 0.75;
  	$idx_90 = $suc_total * 0.90;
  	$idx_95 = $suc_total * 0.95;

		$tw += $_ for @ptime;
		$avgw = ($total == 0)?0:$tw/$total;

  	printf OUT ("|%d|%.2f|%d|%d|%d|%d|%d|%.2f|%d|\n", $k, $ratio, $time_sorted[$idx_25], $time_sorted[$idx_50], $time_sorted[$idx_75], $time_sorted[$idx_90], $time_sorted[$idx_95], $avgw, $total);		
	}

	delete @suc{keys %suc};
	delete @fail{keys %fail};
	delete @suc_time{keys %suc_time};

	close OUT;
