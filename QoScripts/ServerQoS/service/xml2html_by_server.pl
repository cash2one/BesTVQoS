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
$subject = shift @ARGV;

open OUT, ">$outfilename";

sub code_title {
	my ($str) = @_;

    $str .= "<tr>\n";
    $str .= "   <td align=\"left\">响应码</td>\n";
    $str .= "   <td align=\"left\">记录数</td>\n";
    $str .= "   <td align=\"left\">占比</td>\n";
    $str .= "</tr>\n";
}

sub url_title {
        my ($str) = @_;

        $str .= "<tr>\n";
        $str .= "   <td align=\"left\">URL</td>\n";
		$str .= "   <td align=\"left\">200 OK占比</td>\n";
        $str .= "   <td align=\"left\">请求时长P25(s)</td>\n";
        $str .= "   <td align=\"left\">请求时长P50(s)</td>\n";
        $str .= "   <td align=\"left\">请求时长P75(s)</td>\n";
        $str .= "   <td align=\"left\">请求时长P90(s)</td>\n";
        $str .= "   <td align=\"left\">请求时长P95(s)</td>\n";
        $str .= "   <td align=\"left\">平均请求时长(s)</td>\n";
        $str .= "   <td align=\"left\">记录数</td>\n";
        $str .= "</tr>\n";
}

sub hour_title {
        my ($str) = @_;

        $str .= "<h2>按时段分析直播首次缓冲数据</h2>\n";

        $str .= "<tr>\n";
        $str .= "   <td align=\"left\">时段</td>\n";
        $str .= "   <td align=\"left\">缓冲成功率</td>\n";
        $str .= "   <td align=\"left\">P25(ms)</td>\n";
        $str .= "   <td align=\"left\">P50(ms)</td>\n";
        $str .= "   <td align=\"left\">P75(ms)</td>\n";
        $str .= "   <td align=\"left\">P90(ms)</td>\n";
        $str .= "   <td align=\"left\">P95(ms)</td>\n";
        $str .= "   <td align=\"left\">记录数</td>\n";
        $str .= "</tr>\n";
}

$content .= "<!DOCTYPE html>\n";
$content .= "<html lang=\"en\">\n";
$content .= "<head>\n";
$content .= "<meta charset=\"utf-8\" />\n";
$content .= "</head>";

$content .= "<body>\n";

foreach $filename (@ARGV) {

	@sub = split /\//, $filename;
    $content .= "<h3>".$sub[3]." - ".$info{$sub[3]}."</h3>\n";
	$content .= "<table width=\"650\" border=\"1\" cellspacing=\"0\">\n";

	open FILE, "<$filename";

	SWITCH: {
		($subject eq "code") && do {
			$content = code_title($content);
		};

		($subject eq "url") && do {
			$content = url_title($content);
		};

		($subject eq "hour") && do {
            $content = hour_title($content);
        };	
	}

	while (<FILE>) {
		chomp;
		
		@element = split /\|/;
		#$type = $element[0];
		
		# just for url
		if ($subject eq "url") {	
			$r = index($element[1], "OttService");
			if ($r == -1) {
				next;
			}
		}	
		
		$content .= "<tr>\n";

		foreach $key (@element)
		{
			if ($key ne ""){
				$content .= "	<td align=\"left\">".$key."</td>\n";
			}
		}

		$content .= "</tr>\n";
	}
	close FILE;

	
    $content .= "</table>\n";
}

$content .= "</body>\n";
$content .= "</html>\n";


print OUT $content;
