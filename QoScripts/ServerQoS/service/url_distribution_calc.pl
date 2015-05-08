#! /usr/bin/env perl

$svrtype = shift @ARGV;
$svrip = shift @ARGV;
$servicetype = shift @ARGV;
$date = shift @ARGV;
$hour = shift @ARGV;
$key = shift @ARGV;
$written = shift @ARGV;

foreach $filename (@ARGV) {

	open FILE, "<$filename";

	while (<FILE>) {
		chomp;
		@element = split /\|/;

		@sub = split /\?/, $element[6];
		$count{$sub[0]}++;
		
		if ($written == 1) {
			open SUBFILE1, ">>tmp/${svrtype}/${date}/${servicetype}/${svrip}/$sub[0]\_hour";
			print SUBFILE1 $_."\n";
			close SUBFILE1;
			
			if ($hour != 24) {
				open SUBFILE2, ">>tmp/${svrtype}/${date}/${servicetype}/${svrip}/$sub[0]";
				print SUBFILE2 $_."\n";
				close SUBFILE2;
			}
		}
		
		$total += 1;
	}

	close FILE;
}

$outfilename = "${svrtype}/${date}/${servicetype}/${svrip}/distribution_data_${key}_${hour}";
open OUT, ">$outfilename";

foreach $key (sort {$count{$b}<=>$count{$a}} %count) {
	#print $key.",";
	if (defined($key) && defined($count{$key})) {
		printf OUT ("|$key|$count{$key}|%.2f|\n", $count{$key}/$total);
	}
}

close OUT;
