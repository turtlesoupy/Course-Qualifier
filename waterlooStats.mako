<%!
    import WaterlooStats as S
    import datetime
%>

<%
    def percentage( num, denom, dec=1 ):
        return round( float(num) * 100 / denom, dec)
%>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
    <title> Waterloo Statistics </title>
    <link type="text/css" rel="stylesheet" href="css/qualifier.css">
    <link type="text/css" rel="stylesheet" href="css/statistics.css">
	<script type="text/javascript">

	  var _gaq = _gaq || [];
	  _gaq.push(['_setAccount', 'UA-1568225-2']);
	  _gaq.push(['_trackPageview']);

	  (function() {
	    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
	    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	  })();
	</script>
</head>

<body clas='yatta'>
    <div id="container">
    <div class="wrap">
    <div id='headerImage'> <a href="index.html"> <span class="hide"> </span> </a> <h1> Waterloo Course Qualifier </h1><h2> Better than Quest </h2> </div>

    <div class="infobox">
        <p class="introText">
            <span class="bigText">Statistics!</span>
        </p>
        <p class="emailText">
            Last generation: ${datetime.datetime.now().strftime( "%d %b at %I:%M %p" )}
        </p>
    </div>



    <div class='statWidgetGroup'>

        <div class="floatedStatWidget">
            <h2> Popular pairs </h2>
            <div class="statWidgetText">
                %for (course1, course2), num in S.popularPairs():
                    ${course1} and ${course2} (${num}) <br />
                %endfor
            </div>
        </div>

        <div class="floatedStatWidget">
            <h2> Most conflicting </h2>
            <div class="statWidgetText">
                %for course1, course2, num in S.oftenConflicting():
                    ${course1} and ${course2} (${num}) <br />
                %endfor
            </div>
        </div>
    </div>

    <div class="statWidget">
        <h2> Requests By Subject</h2>
        <div class="floatedChartDiv">
            ${S.subjectChart()}
        </div>
        <div class="statWidgetText">
            <table>
                %for subject,num in S.subjectNumbers():
                   <tr>
                        <td> ${subject} </td> 
                        <td> ${percentage( num, S.numRequestCourses() )}% (${num})</td>
                   </tr>
                %endfor
            </table>
        </div>
    </div>
    

    <div class="statWidget">
        <h2> Requests By Courses </h2>
        <div class="floatedChartDiv">
            ${S.courseChart()}
        </div>
        <div class="statWidgetText">
            <table>
                %for subject, course, num in S.courseNumbers():
                    <tr>
                        <td> ${subject} ${course} </td>
                        <td> ${percentage( num, S.numRequestCourses() )}% (${num}) </td>
                    </tr>
                %endfor
            </table>
        </div>
    </div>

    <div class='statWidgetGroup'>
        <h2> Numerical </h2>
        Number of requests ${S.numRequests()} <br />
        Number of request courses ${S.numRequestCourses()} <br />
        Average courses per request ${round(float(S.numRequestCourses()) / S.numRequests(),1) } <br />
    </div>

    </div>
    </div>
</body>

</html>
