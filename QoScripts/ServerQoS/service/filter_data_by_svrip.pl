#! /usr/bin/env perl

$svrtype = shift @ARGV;
$date = shift @ARGV;
$hour = shift @ARGV;
$key = shift @ARGV;
$written = shift @ARGV;

$infofile = shift @ARGV;
open FILE, "<$infofile";
while (<FILE>) {
	chomp;
	
	@element = split /\s+/;
	$info{$element[1]} = $element[0];

	`mkdir -p tmp/${svrtype}/${date}/$element[0]`;
}
close FILE;

foreach $filename (@ARGV) {

	open FILE, "<$filename";
	#print $filename."\n";

	while (<FILE>) {
		chomp;
		@element = split /\|/;

		@sub = split / /, $element[0];
		$svrip = pop @sub;
	
		$count{$svrip}++;
		
		if ($written == 1) {
			open SUBFILE1, ">>tmp/${svrtype}/${date}/$info{${svrip}}/${svrip}_hour";
			print SUBFILE1 $_."\n";
			close SUBFILE1;
			
			if ($hour != 24) {
				open SUBFILE2, ">>tmp/${svrtype}/${date}/$info{${svrip}}/${svrip}_all";
				print SUBFILE2 $_."\n";
				close SUBFILE2;
			}
		}
		
		$total += 1;
	}

	close FILE;
}

$outfilename = "$svrtype/$date/distribution_data_${key}_${hour}";
open OUT, ">$outfilename";

foreach $key (sort {$count{$b}<=>$count{$a}} %count) {
	#print $key.",";
	if (defined($key) && defined($count{$key})) {
		printf OUT ("|$key|$info{${key}}|$count{$key}|%.2f|\n", $count{$key}/$total);
	}
}

#print OUT "|total|$total|\n";

close OUT;
