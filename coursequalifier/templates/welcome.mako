<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
    <title> Waterloo Course Qualifier </title>
    <!-- Combo-handled YUI CSS files: --> 
    <!-- Combo-handled YUI JS files: --> 
    ${h.stylesheet_link('http://yui.yahooapis.com/combo?2.8.1/build/fonts/fonts-min.css&2.8.1/build/container/assets/skins/sam/container.css&2.8.1/build/datatable/assets/skins/sam/datatable.css')}
    ${h.javascript_link('http://yui.yahooapis.com/combo?2.8.1/build/utilities/utilities.js&2.8.1/build/container/container-min.js&2.8.1/build/datasource/datasource-min.js&2.8.1/build/datatable/datatable-min.js&2.8.1/build/json/json-min.js')}
    ${h.stylesheet_link('/css/qualifier.css')}
    ${h.javascript_link('/js/qualifier.js')}

    <meta name="title" content="Waterloo Course Qualifier" />
    <meta name="description" content="A simple way to select your courses by way of sorting all possible schedules on specific metrics, like number of days off, or how early each class starts." />
    <link rel="image_src" href="/qualifier.jpg" />

    <style>
    .yui-overlay { position:absolute;background:#fff;border:1px dotted black;padding:5px;margin:10px; }
    .yui-overlay .hd { border:1px solid red;padding:5px; }
    .yui-overlay .bd { border:1px solid green;padding:5px; }
    .yui-overlay .ft { border:1px solid blue;padding:5px; }

    #ctx { background:orange;width:100px;height:25px; }
    
    #example {height:15em;}
    </style>
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
<body class="yui-skin-sam">
<div id="container">
    <div class="wrap">
        <div id='headerImage'> <a href="index.html"> <span class="hide"> </span> </a> <h1> Waterloo Course Qualifier </h1><h2> Better than Quest </h2> </div>
        <div class="infobox">
                <p class="introText">
                The Course Qualifier helps you generate all possible course timetables without time conflicts. You can choose a path that allows you to make the <em>most efficient</em> use of your time. 
                </p>
                <p class="emailText">
                Source now available on <a href="http://github.com/cosbynator/Course-Qualifier">github</a>. <a href="http://develop.feds.ca/projects/course-qualifier">Project issues</a> on Feds SDN.
		<br />
		<br />
                <script>function fbs_click() {u=location.href;t=document.title;window.open('http://www.facebook.com/sharer.php?u='+encodeURIComponent(u)+'&t='+encodeURIComponent(t),'sharer','toolbar=0,status=0,width=626,height=436');return false;}</script><style> html .fb_share_link { padding:2px 0 0 20px; height:16px; background:url(http://static.ak.fbcdn.net/images/share/facebook_share_icon.gif?2:26981) no-repeat top left; }</style><a href="http://www.facebook.com/share.php?u=http://www.coursequalifier.com" onclick="return fbs_click()" target="_blank" class="fb_share_link">Facebook</a>, 
<a href="http://del.icio.us/post?url=http://www.coursequalifier.com&title=Waterloo%20Course%20Qualifier">
		<img border="0" src="http://images.del.icio.us/static/img/delicious.small.gif" />
		Del.icio.us</a>, 
		etc.
                <br />
                </p>
        </div>

        <p class="emailText">
        </p>
        <h2> Select Your Courses: </h2>

        <form id="course_form" method="POST">
            <input type="hidden" name="school" value="waterloo" />
            Term:
            <select class="term" name="term">
                <option value="1099">Fall 2009</option>
                <option value="1101">Winter 2010</option>
                <option value="1105">Spring 2010</option>
                <option value="1109">Fall 2010</option>
                <option value="1111" selected="selected">Winter 2011</option>
                <option value="1115">Spring 2011</option>
            </select>

            <a href="advanced" id="advanced_options_toggle">Advanced Options...</a>
            <br />
            <br />
            <div id="course_list">
                <div class="course">
                    Course: <input type="text" class"course_query" name="course_query" value="CS 245" />
                    <span class="options">
                        Tutorials: <input type="checkbox" class="tutorials" name="tutorials" checked="checked" />
                        Tests:     <input type="checkbox" class="tutorials" name="tests" />
                        Other:     <input type="checkbox" class="tutorials" name="other" checked="checked" />
                        Sections:  
                        <input type="text" class="course_section" name="sections[]" />
                        <input type="text" class="course_section" name="sections[]" />
                        <input type="text" class="course_section" name="sections[]" /> (e.g. 101)
                    </span>
                </div>
                <div class="course">
                    Course: <input type="text" class"course_query" name="course_query" value="" />
                    <span class="options">
                        Tutorials: <input type="checkbox" class="tutorials" name="tutorials" checked="checked" />
                        Tests:     <input type="checkbox" class="tutorials" name="tests" />
                        Other:     <input type="checkbox" class="tutorials" name="other" checked="checked" />
                        Sections:  
                        <input type="text" class="course_section" name="sections[]" />
                        <input type="text" class="course_section" name="sections[]" />
                        <input type="text" class="course_section" name="sections[]" />
                    </span>
                </div>
                <div class="course">
                    Course: <input type="text" class"course_query" name="course_query" value="" />
                    <span class="options">
                        Tutorials: <input type="checkbox" class="tutorials" name="tutorials" checked="checked" />
                        Tests:     <input type="checkbox" class="tutorials" name="tests" />
                        Other:     <input type="checkbox" class="tutorials" name="other" checked="checked" />
                        Sections:  
                        <input type="text" class="course_section" name="sections[]" />
                        <input type="text" class="course_section" name="sections[]" />
                        <input type="text" class="course_section" name="sections[]" />
                    </span>
                </div>
                <div class="course">
                    Course: <input type="text" class"course_query" name="course_query" value="" />
                    <span class="options">
                        Tutorials: <input type="checkbox" class="tutorials" name="tutorials" checked="checked" />
                        Tests:     <input type="checkbox" class="tutorials" name="tests" />
                        Other:     <input type="checkbox" class="tutorials" name="other" checked="checked" />
                        Sections:  
                        <input type="text" class="course_section" name="sections[]" />
                        <input type="text" class="course_section" name="sections[]" />
                        <input type="text" class="course_section" name="sections[]" />
                    </span>
                </div>
                <div class="course">
                    Course: <input type="text" class"course_query" name="course_query" value="" />
                    <span class="options">
                        Tutorials: <input type="checkbox" class="tutorials" name="tutorials" checked="checked" />
                        Tests:     <input type="checkbox" class="tutorials" name="tests" />
                        Other:     <input type="checkbox" class="tutorials" name="other" checked="checked" />
                        Sections:  
                        <input type="text" class="course_section" name="sections[]" />
                        <input type="text" class="course_section" name="sections[]" />
                        <input type="text" class="course_section" name="sections[]" />
                    </span>
                </div>
            </div>
            <a href="" id="add_course" >Add course</a>
            <br />
            <br />
            <input type="submit" value="Make it so!" id="submit_courses" />
        </form>

        <div id="info_area">
        </div>

        <div id="trace_area">
        </div>

        <div id="error_area">
        </div>

        <div id="too_many_explanation">
            <h3>Up to <span id="too_many_number">1000</span> possible schedules!</h3>

            Make the query more restrictive! Select any of the <b>advanced options</b> and try to reduce possibilities! 

            <p class="fine_print">Large numbers of choices quickly overload the system as well as the display. Try to keep it reasonable, by
            setting a minimum start time / minimum end time or selecting specific sections of courses.</p>
        </div>


        <div id="result_area">
            <h2> Select a course sequence: </h2>
            <a href="" id="show_conflicts"></a> <span id="show_conflicts_number"></span>
            <div id="conflict_area">
            </div>

            <div id="qualifier_grid">
                Awaiting course selection... 
            </div>

            <a name="qualify_calendar_anchor"></a>
            <h2> Course timetable / details: </h2>
            <div id="create_pdf_div" style="display:none;"> 
                <a href="" id="create_pdf"><img src="/images/pdf.png" border="0" /> PDF Version (Printable)</a>
                <br />
            </div>
            <div id="qualifier_calendar">
                Awaiting row selection... 
            </div>

            <div id="row_select" style="display: none;">
                <div class ="row_select_info">
                    Row: <span id="row_select_number"></span> <br />
                </div>
                <a href="" id="select_previous_row">Previous</a> | 
                <a href="" id="select_next_row">Next</a>
            </div>
            <div id="catalog_information">

            </div>
            <div class="clear"> </div>
            <br />
            <br />

            <form name="pdf_form" target="_blank" action="/schedule/pdf" method="POST">
            <input type="hidden" name="ugly_url" />
            </form>
        </div>
    </div>
</div>

<div id="footer">
  <div class="wrap">
    <div class="help">
      <h2>How to use Course Qualifier</h2>
      <br />
      Simple:
        <ol>
        <li> Pick some courses you might wish to take from the <a href="http://ugradcalendar.uwaterloo.ca/">Undergraduate Course Calendar</a> </li>
        <li> From the course qualifier, pick your term (Winter 2011, etc.) </li>

        <li> Enter your course subject followed by course number (ex. AMATH 250)
        <li> Press <em>Make it so</em> and sort by a desired column </li>

        <li> Highlight the row of your course sequence and click. Mysteriously, a possible schedule appears!</li>
    </ol>

    <p>
    Want more control? Toggle <em>Advanced Options</em>! 
    </p>

    <p>
        Too many results? Filter some out! <br />
        
        Click <em>advanced options</em> and start filtering. You can mandate specific sections
        by typing their course code (like MATH 135 101 and 001). It also may be handy to <em>hide full courses</em>.
    </p>

    <p>
        Statisfied with your schedule? Make a PDF out of it by clicking "PDF Version".
    </p>

    </div>

    <div class="meta">
      <h2>About Course Qualifier</h2>
      <p> The course qualifier is a <s>quick</s> longish <a href="http://www.python.org/">Python</a> service using the <a href="http://http://pylonshq.com/">Pylons</a> framework.
      Originally, it was a bit of a hack but it has been maintained very passively since April 2007 since people seem to like it. </p>

      The table fields are as follows:
      <ul>
        <li> Days of class: number of days that have any class at all
        <li> Time between classes: time spent <i>between</i> classes in a day.
        <li> Earliest start time: earliest start of a class in the week</li>
        <li> Latest start time: latest end of a class in the week</li>
        <li> Lateness: how close you are to having all your classes end at midnight (as a percentage) </li>
        </li>

    </ul>
      <h2>Disclaimer</h2>

      <p> Despite my best efforts, there is no foolproof method of preventing bad schedules, profs, early mornings, confusing non-sequiturs or Urkel. </p>
      <p>To the best of my knowledge, this is not official University of Waterloo software. </p>
      <br /><a href="http://www.uwaterloo.ca/">${h.image("/images/uwlogo.jpg", "UW", class_="uwlogo")}</a>
      <p>&copy;2011 <a href="http://www.thomasdimson.com/">Thomas Dimson</a>, design by <a href="http://donmckenzie.ca/">Don McKenzie</a>
      <span class="noemphasis">
          Last updated January 6, 2011 (data updated with <a href="http://www.uwdata.ca">uwdata.ca</a>) - <a href="changelog.txt">Changelog</a> 
      </span>
      </p>
    </div>
</div>

<div id="advanced_options" style="visibility:hidden; ">
    <table class="advanced_options_table">
    <!--
    <tr>
        <td>Show distance education courses:</td>
        <td><input type="checkbox" id="show_distance_ed" class="show_distance_ed" name="show_distance_ed" /></td>
    </tr>
    -->
    <tr>
        <td>Show full courses:</td>
        <td><input type="checkbox" id="show_full_courses" class="show_full_courses" name="show_full_courses" checked="checked" /></td>
    </tr>
    <tr>
        <td> Classes start later than: </td>
        <td> 
             <select id="starts_later_than_hour" name="starts_later_than_hour">
                <option value="">--</option> 
                <option value="1">1</option> 
                <option value="2">2</option> 
                <option value="3">3</option> 
                <option value="4">4</option> 
                <option value="5">5</option> 
                <option value="6">6</option> 
                <option value="7">7</option> 
                <option value="8">8</option> 
                <option value="9">9</option> 
                <option value="10">10</option> 
                <option value="11">11</option> 
                <option value="12">12</option> 
             </select>:<select id="starts_later_than_minute" name="starts_later_than_minute">
                <option value="" selected="selected">--</option>
                <option value="0">00</option>
                <option value="30">30</option>
            </select>
            <select id="starts_later_than_ampm" name="starts_later_than_ampm">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
            </select>

        </td>
    </tr>
    <tr>
        <td> Classes end earlier than: </td>
        <td>
             <select id="ends_earlier_than_hour" name="ends_earlier_than_hour">
                <option value="">--</option> 
                <option value="1">1</option> 
                <option value="2">2</option> 
                <option value="3">3</option> 
                <option value="4">4</option> 
                <option value="5">5</option> 
                <option value="6">6</option> 
                <option value="7">7</option> 
                <option value="8">8</option> 
                <option value="9">9</option> 
                <option value="10">10</option> 
                <option value="11">11</option> 
                <option value="12">12</option> 
             </select>:<select id="ends_earlier_than_minute" name="ends_earlier_than_minute">
                <option value="" selected="selected">--</option>
                <option value="0">00</option>
                <option value="30">30</option>
            </select>
            <select id="ends_earlier_than_ampm" name="ends_earlier_than_ampm">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
            </select>

        </td>
    </table>
</div>
</body>
</html>
