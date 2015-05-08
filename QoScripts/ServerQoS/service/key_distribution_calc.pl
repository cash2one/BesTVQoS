#! /usr/bin/env perl

$svrtype = shift @ARGV;
$svrip = shift @ARGV;
$servicetype = shift @ARGV;
$date = shift @ARGV;
$hour = shift @ARGV;
$key = shift @ARGV;
$idx = shift @ARGV;
$written = shift @ARGV;

foreach $filename (@ARGV) {

	open FILE, "<$filename";
	#print $filename."\n";

	while (<FILE>) {
		chomp;
		@element = split /\|/;

		$count{$element[$idx]}++;
		
		if ($written == 1) {
			open SUBFILE1, ">>tmp/${svrtype}/${date}/${servicetype}/${svrip}/$element[$idx]\_hour";
			print SUBFILE1 $_."\n";
			close SUBFILE1;
		}
		
		$total += 1;
	}

	close FILE;
}

$outfilename = "$svrtype/$date/${servicetype}/$svrip/distribution_data_${key}_${hour}";
open OUT, ">$outfilename";

foreach $key (sort {$count{$b}<=>$count{$a}} %count) {
	#print $key.",";
	if (defined($key) && defined($count{$key})) {
		printf OUT ("|$key|$count{$key}|%.2f|\n", $count{$key}/$total);
	}
}

#print OUT "|total|$total|\n";

close OUT;
