#! bin/perl

$infofile = shift @ARGV;
open FILE, "<$infofile";
while (<FILE>) {
        chomp;

        @element = split /\s+/;
        $info{$element[1]} = $element[0];
}
close FILE;


$outfilename = shift @ARGV;

open OUT, ">$outfilename";

foreach $filename (@ARGV) {
	
	open FILE, "<$filename";

	$content .= "<!DOCTYPE html>\n";
	$content .= "<html lang=\"en\">\n";
	$content .= "<head>\n";
	$content .= "<meta charset=\"utf-8\" />\n";
	$content .= "</head>";

	$content .= "<body>\n";	
	$content .= "<table width=\"650\" border=\"1\" cellspacing=\"0\">\n";

	while (<FILE>) {
		chomp;
		
		@element = split /\|/;
		#$type = $element[0];
	
		if (defined($info{$element[1]})) {
			unshift @element, $info{$element[1]};		
		}

		$content .= "<tr>\n";

		foreach $key (@element)
		{
			#print $key."\n";
			if ($key ne ""){
				$content .= "	<td align=\"left\">".$key."</td>\n";
			}
		}

		$content .= "</tr>\n";
	}
	
	$content .= "</table>\n";

	$content .= "<br>\n";
	
	$content .= "</body>\n";
	$content .= "</html>\n";
	
}

print OUT $content;
