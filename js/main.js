// Define global variables
$.ajaxSetup({async:false});

$.getJSON('json/full_data.json', function(data){
	county_data = data;
});

$.getJSON('json/counties_list.json', function(data){
	counties_list = object_to_array(data);
});

var current_graph = 'Rep_Percent';

var current_object = '';

var color_list = ['color_purple','color_green','color_orange','color_blue','color_red']

// Determine Number Text Ending
function number_ender(num) {
	num = String(num);
	last = num.substr(num.length - 1);
	if (last == "1") {
		return "st";
	} else if (last == "2") {
		return "nd";
	} else if (last== "3") {
		return "rd";
	} else {
		return "th";
	}
}

// Randomly Shuffle Array
function shuffle(array) {
	var currentIndex = array.length, temporaryValue, randomIndex ;
	while (0 !== currentIndex) {
		randomIndex = Math.floor(Math.random() * currentIndex);
		currentIndex -= 1;
		temporaryValue = array[currentIndex];
		array[currentIndex] = array[randomIndex];
		array[randomIndex] = temporaryValue;
	}
	return array;
}

// Create AJAX loader
(function(){
	var spin_opts = { lines: 13, length: 13, width: 3, radius: 15, corners: 0, rotate: 0, direction: 1, color: '#000', speed: 1, trail: 42, shadow: false, hwaccel: false, className: 'ajax-spinner', zIndex: 2e9, top: '50%', left: '50%', color: '#2171b5' };
	var target = document.getElementById('ajax-loader');
	var spinner = new Spinner(spin_opts).spin(target);
}());

// Create feature-box dropdown
(function() {
	$(".feature-box").append('<select id="feature-select"><option val="feature">All</option></select>')
	for (item of categories.sort()) {
		$("#feature-select").append("<option val='" + item + "'>" + item.replace("_", " ") + "</option>");
	}
}());

// Generate features list
function generate_features() {
	var labels = {};
	var new_names = [];
	var new_labels = [];
	for (var key in label_info) {
		labels[label_info[key][0]] = key;
		new_names.push(label_info[key][0]);
	}
	for (name of new_names.sort()) {
		new_labels.push(labels[name]);
	}
	return new_labels;
};

var features = generate_features();

// Generate features for .features_list
(function() {
	for (item of features ) {
		var obj_name = item;
		var classes = "feature";
		for (category of label_info[obj_name][2]) {
			classes += " ";
			classes += category;
		}
		var bold = '';
		if(item == "Rep_Percent"){ bold = "style='font-weight: bold;'"; }
		$(".features_list").append("<li class='" + classes + "'" + bold + " key=" + item + ">" + label_info[item][0] + "</li>");
	}
}());

// Change title based on current_object
function change_title() {
  var new_title = label_info[current_graph][0];
  var scales = ($('input[name=scales]:checked').val())
  $("#graph-title").text(new_title + " (" + scales + "d)");
}

// Get high and low of current graph
function get_high_low() {
	var all_paths = document.getElementsByTagName("path");
	for(var key in all_paths) {
		if (key < 3141) {
			var fips = all_paths[key].__data__.id;
		    var data = county_data[current_graph][fips];
			if (key == 0) {
				var low = data;
				var high = data;
			} else {
				if (data < low) {
					low = data;
					low_fips = fips;
				}
				if (data > high) {
					high = data;
					high_fips = fips;
				}
			}
		}
	}
	return [low, high, low_fips, high_fips];
}

function get_feature_percentile(feature, fips) {
	var data = county_data[feature];
	var low = data[1001];
	var high = data[1001];
	for(var key in data) {
		if (data[key] < low) {
			low = data[key];
		}
		if (data[key] > high) {
			high = data[key];
		}
	}
	if (low == 0) {
		low = 0.00001;
	}
	var range = high - low;
	var diff = data[fips] - low;
	var percentile = shorten_string((diff/range)*100);
	return percentile;
}

// Generate Map
(window.create_map = function(filename, classname, scale, w, h) {
	$("#ajax-loader").show();

	// Define default parameters
	if (typeof(w)==='undefined') w = 960;
	if (typeof(h)==='undefined') h = 600;

	// First empty the canvas
	$("." + classname).empty();

	var width = w,
		height = h;

	var rateById = d3.map();

	var quantize = d3.scale.quantize()
		.domain(scale)
		.range(d3.range(9).map(function(i) { return "b" + i; }));

	var projection = d3.geo.albersUsa()
		.scale(1280)
		.translate([width / 2, height / 2]);

	var path = d3.geo.path()
		.projection(projection);

	var svg = d3.select('.' + classname).append("svg")
		.attr("width", width)
		.attr("height", height);

	queue()
		.defer(d3.json, "json/us.json")
		.defer(d3.tsv, filename, function(d) { rateById.set(d.id, +d.rate); })
		.await(ready);

	function ready(error, us) {
		svg.append("g")
			.attr("class", "counties")
			.selectAll("path")
			.data(topojson.feature(us, us.objects.counties).features)
			.enter()
			.append("path")
			.attr("transform", "translate(-1000)")
			.attr("class", function(d) { return quantize(rateById.get(d.id))})
			.attr("d", path)

	    svg.append("path")
	        .datum(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; }))
	        .attr("transform", "translate(-1000)")
	        .attr("class", "states")
	        .attr("d", path)

	    var paths = d3.selectAll("path");
		for(var key in shuffle(paths[0])) {
			d3.select(paths[0][key]).transition().duration(800).delay(key/5).attr("transform", "translate(0)");
		}

	    highlight_current_county();
	    if($("#show-party").attr("show") == "1") {
	    	add_parties();
	    }
	    var color = $("#switch-colors").attr("color");
	    if(color != "bw") {
	    	switch_colors(color);
	    }

	    $("#ajax-loader").hide();

	    // Create Legend<div key='" + legend[2] + "'>
		var legend = get_high_low();
		$("#low-legend").html("<b>" + shorten_string(legend[0]) + "</b><br>(" + county_data.County[legend[2]] + ", " + county_data.State[legend[2]] + ")").attr("key", legend[2]);
		$("#high-legend").html("<b>" + shorten_string(legend[1]) + "</b><br>(" + county_data.County[legend[3]] + ", " + county_data.State[legend[3]] + ")").attr("key", legend[3]);
		$('html, body').animate({scrollTop:0}, 'slow');
	}

	d3.select(self.frameElement).style("height", height + "px");

})('tsv/Normalized_Rep_Percent.tsv', 'svg', [-3,3])

// Create Canvas and Map
function create_canvas(obj, current){
	var paths = d3.selectAll("path");
	for(var key in shuffle(paths[0])) {
		d3.select(paths[0][key]).transition().duration(800).delay(key/5).attr("transform", "translate(-1000)");
	}
	scales = ($('input[name=scales]:checked').val());
	var index = (current == 1) ? obj.attr('key') : current_graph;
	var domain = (scales == "Normalize") ? [-3,3] : [0,1];
	filename = 'tsv/' + scales + 'd_' + index + '.tsv';
	current_graph = index;
	setTimeout(
		function() {
			create_map(filename, 'svg', domain);
		}, 1200);
	change_title();
	$("#feature-desc").html(label_info[index][1]);
}


// Turn object into an array
function object_to_array(object) {
	var arr = []
	for (var key in object) {
		arr.push(object[key]);
	}
	return arr;
}

// Highlight currently selected county on map
function highlight_current_county() {
	if (current_object !== '') {
		var id = current_object.__data__.id;
		current_object.__data__.native_color = current_object.style.fill;
		var all_paths = document.getElementsByTagName("path");
		for(var key in all_paths) {
			if (key < 3141) {
			    if(all_paths[key].__data__.id == id){
			    	current_object = all_paths[key]
			    	break;
			    }
			}
		}
		d3.select(current_object).attr({"stroke":"#76EE00","stroke-width":"2px"});
	}
}

// Remove highlight from current ojbect
function unhighlight_current_county() {
	if (current_object !== '') {
		var nat_col = current_object.__data__.native_color;
		d3.select(current_object).attr({"stroke":"none", "stroke-width":"0", "fill":nat_col});
	}
}

// Remove highlight from current ojbect
function unhighlight_all_counties() {
	var all_paths = document.getElementsByTagName("path");
	for(var key in all_paths) {
		if (key < 3141) {
			var obj = d3.select(all_paths[key]);
		    if(obj.attr("stroke") == "#76EE00" || obj.attr("stroke") == "rgb(118, 238, 0)"){
		    	obj.attr({"stroke":"none", "stroke-width":"0"});
		    }
		}
	}
}

// Add Party Colors
function add_parties() {
	var all_paths = document.getElementsByTagName("path");
	for(var key in all_paths) {
		if (key < 3141) {
			var fip = all_paths[key].__data__.id;
			var vote = county_data.Voted[fip];
			var class_list = all_paths[key].classList;
			var classes = "vote" + vote + " ";
			for (_class of class_list) {
				classes += _class;
				classes += " ";
			}
			$(all_paths[key]).attr("class", classes);
		}
	}
	$("#show-party").attr("show", "1");
}

// Remove party colors
function remove_parties() {
	var all_paths = document.getElementsByTagName("path");
	for(var key in all_paths) {
		if (key < 3141) {
			var fip = all_paths[key].__data__.id;
			var vote = county_data.Voted[fip];
			var class_list = all_paths[key].classList;
			var classes = "";
			for (_class of class_list) {
				if ((_class !== "vote0") && (_class !== "vote1")) {
					classes += _class;
					classes += " ";
				}
			}
			$(all_paths[key]).attr("class", classes);
		}
	}
	$("#show-party").attr("show", "0");
	var color = $("#switch-colors").attr("color");
	switch_colors(color);
}

// Generate Info Block
function gen_info_block(fips) {
	$(".info-block").append("<h2> Info for <b class='blue'>" + county_data.County[fips] + ", " + county_data.State[fips] + "</b></h2>");
	var val = county_data[current_graph][fips];
	var cur_percentile = Math.round(get_feature_percentile(current_graph, fips));
	$(".info-block").append("<p id='feature-info'><span class='rank-width'></span><span class='rank'>" + cur_percentile + "<span>" + number_ender(cur_percentile) + "</span></span><span class='feature-info-text'><b>" + shorten_string(val) + " " + label_info[current_graph][0] + ":</b> " + label_info[current_graph][1] + "</span></p>");
	var rank_width = String(cur_percentile*10.09) + "px";
	$("#feature-info > .rank-width").css("width",rank_width);
	for (item of features) {
		var obj_name = item;
		var feature_num = county_data[obj_name][fips];
		var classes = "feature";
		for (category of label_info[obj_name][2]) {
			classes += " ";
			classes += category;
		}
		var percentile = get_feature_percentile(obj_name, fips);

		$(".info-block").append("<p class='" + classes + "' key=" + item + "><span class='percentile'>" + Math.round(percentile) + "</span>" + label_info[obj_name][0] + ": <b>" + shorten_string(feature_num) + "</b></p>");
	}
	$(".info-block").slideDown();
	$(".info-block").append('<span class="blue" id="close-info">X</span>');
	$(".info-block").append('<p id="select-category-text">Filter by Category</p>');
	$(".info-block").append('<select id="category-select"><option val="feature">All</option></select>')
	for (item of categories.sort()) {
		$("#category-select").append("<option val='" + item + "'>" + item.replace("_", " ") + "</option>");
	}
	$(".feature[key=" + current_graph + "]").css({"font-weight":"bold","font-style":"normal"});
	$("#category-select").val("Interesting").trigger('change');
	$("#feature-select").val("Interesting").trigger('change');
}

//Remove path-hovered from single object
function remove_hover(obj) {
	var class_list = obj.classList;
	var classes = "";
	for (_class of class_list) {
		if(_class !== "path-hovered") {
			classes += _class;
			classes += " ";
		}
	}
	$(obj).attr("class", classes);
}
//Remove class path-hovered from all objects
function remove_all_hover() {
	var hovered_paths = document.getElementsByClassName("path-hovered");
	for(var i = 0; i < hovered_paths.length; i++) {
		remove_hover(hovered_paths[i]);
	}
	var all_paths = document.getElementsByTagName("path");
	for(var key in all_paths) {
		if (key < 3141) {
		    if(all_paths[key].style.fill == '#76EE00' || all_paths[key].style.fill == "rgb(118, 238, 0)"){
		    	all_paths[key].style.fill = all_paths[key].__data__.native_color;
		    }
		}
	}
}

// Switch map color
function switch_colors(color) {
	var all_paths = document.getElementsByTagName("path");
	for(var key in all_paths) {
		if (key < 3141) {
			var class_list = all_paths[key].classList;
			var classes = color + " ";
			for (_class of class_list) {
				if(color_list.indexOf(_class) == -1) {
					classes += _class;
					classes += " ";
				}
			}
			$(all_paths[key]).attr("class", classes);
		}
	}
	$("#switch-colors").attr("color", color);
	var all_legend = document.getElementsByClassName("legend-box");
	for(var box in all_legend) {
		var class_list = all_legend[box].classList;
		var classes = color + " ";
		if (typeof class_list !== "undefined") {
			for (_class of class_list) {
				if(color_list.indexOf(_class) == -1) {
					classes += _class;
					classes += " ";
				}
			}
		}
		$(all_legend[box]).attr("class", classes);
	}
}

// Return map color to b&w
function return_to_bw() {
	var all_paths = document.getElementsByTagName("path");
	for(var key in all_paths) {
		if (key < 3141) {
			var class_list = all_paths[key].classList;
			var classes = "";
			for (_class of class_list) {
				if(color_list.indexOf(_class) == -1) {
					classes += _class;
					classes += " ";
				}
			}
			$(all_paths[key]).attr("class", classes);
		}
	}
	$("#switch-colors").attr("color", "bw");
	var all_legend = document.getElementsByClassName("legend-box");
	for(var box in all_legend) {
		var class_list = all_legend[box].classList;
		var classes = "";
		if (typeof class_list !== "undefined") {
			for (_class of class_list) {
				if(color_list.indexOf(_class) == -1) {
					classes += _class;
					classes += " ";
				}
			}
		}
		$(all_legend[box]).attr("class", classes);
	}
}

// Tool Tips
function remove_tip(classname) {
	$("." + classname).on("mouseenter", function() {
		setTimeout(
			function() {
				$("." + classname).removeClass(classname);
			}, 5000);
	});
}

// Short strings over 5
function shorten_string(str) {
	str = parseFloat(str);
	str = (str % 1 != 0) ? str.toFixed(2) : str;
	if(str.length > 5) {
		return str.substring(0,4);
	}
	return str;
}

// Set current object by fips
function set_current_object(fips) {
	var all_paths = document.getElementsByTagName("path");
	for(var i=0; i < all_paths.length; i++) {
		if (i < 3141) {
		    if(all_paths[i].__data__.id == fips){
		    	current_object = all_paths[i];
		    	break;
		    }
		}
	}
}

// Create all tooltips
(function() {
	var tooltips = [['feature-tip','See a map for a different feature'],['search-tip','Search for different counties'],['party-tip','Display which counties voted for which political party'],['color-tip','The world will explode. I warned you.'],['info-tip','How to use this site']];
	for(var i = 0; i < tooltips.length; i++) {
		Tipped.create("." + tooltips[i][0],tooltips[i][1]);
	}
	Tipped.create(".switch","'Regular' removes the lowest and highest 0.1% of data. 'Outliers' includes all data, even the most extreme numbers.");
	Tipped.create(".percentile", "The percentile amongst all other counties.");
}());

$("#get-info").on("click",function() {
	var show = $(this).attr("show");
	if (show == "0") {
		$("#use-block").slideDown();
		$(this).attr("show","1");
		$(".svg").css("opacity","0.15");
		$("#county-name").css("opacity","0");
		$(this).text("X");
	} else {
		$("#use-block").slideUp();
		$(this).attr("show","0");
		$(".svg").css("opacity","1");
		$("#county-name").css("opacity","1");
		$(this).text("How to Use");
	}
});
// Generate new map for feature
$(".features_list > li").on("click", function(){
	$(".features_list > li").css("font-weight", "normal");
	$(".feature > i").css("font-weight", "normal");
	$(".chosen_feature").css("font-weight", "normal");
	$(this).css("font-weight", "bold");
	current_graph = $(this).attr("key");
	scales = ($('input[name=scales]:checked').val());
	create_canvas($(this), 1);
	$(".feature-box").slideUp();
	$(this).attr("show","0");
	$(".svg").css("opacity","1");
	$("#county-name").css("opacity","1");
	$("#get-features").text("Change Map");
	$(".feature[key=" + current_graph + "] > i").css({"font-weight" : "bold","font-style" : "normal"});
});

// Add italics on hover of feature
$(".features_list > li").hover(function(){
	$(this).css("font-style", "italic");
	}, function(){
	$(this).css("font-style", "normal");
});

// Generate graph when switching between normalized and scaled
$(".switch-input").on("change", function(){
	create_canvas($(this), 0);
});

// Switch color to red for Republican Counties
$("#show-party").on('click', function(){
	// return_to_bw();
	if($("#show-party").attr("show") == "0") {
		add_parties();
	} else {
		remove_parties();
	};
});

// Toggle to Purple Color
$("#switch-colors").on('click', function(){
	if($(this).attr("color") == "bw") {
		switch_colors('color_purple');
	} else if($(this).attr("color") == "color_purple") {
	 	switch_colors('color_green');
	} else if($(this).attr("color") == "color_green") {
	 	switch_colors('color_orange');
	} else if($(this).attr("color") == "color_orange") {
	 	switch_colors('color_blue');
	} else if($(this).attr("color") == "color_blue") {
	 	switch_colors('color_red');
	}  else {
		return_to_bw();
	}
});

// Display county name and state and highlight red on mouseover
$(".svg").on({
    mouseenter: function() {
		var fips = this.__data__.id;
		var native_color = this.style.fill;
		this.__data__.native_color = native_color;
		var class_list = this.classList;
		var classes = "path-hovered ";
		for (_class of class_list) {
			if(_class !== "path-hovered") {
				classes += _class;
				classes += " ";
			}
		}
		$(this).attr("class", classes);
		if (typeof fips !== 'undefined') {
			color = $(this).css("fill");
			$(this).css("fill","#76EE00");
			$("#county-name").html(label_info[current_graph][0] + " for <br>" + county_data.County[fips] + ", " + county_data.State[fips] + ": <b>" + shorten_string(county_data[current_graph][fips]) + "</b>");
		}
    }, mouseleave: function() {
		if (this !== current_object) {
			var class_list = this.classList;
			var classes = "";
			for (_class of class_list) {
				if(_class !== "path-hovered") {
					classes += _class;
					classes += " ";
				}
			}
			$(this).attr("class", classes);
		}
		var fips = this.__data__.id;
		var native_color = this.__data__.native_color;
		if (typeof fips !== 'undefined') this.style.fill = native_color;
		$("#county-name").text("");
    }
}, "path");


// Open info about county on map click
$(".svg").on("click", "path", function(){
	var fips = this.__data__.id;
	if (typeof fips !== 'undefined') {
		remove_all_hover();
		unhighlight_current_county();
		$(".info-block").empty();
		current_object = this;
		var nat_col = this.__data__.native_color;
		d3.select(this).attr({"stroke":"#76EE00","stroke-width":"2px"});
		this.style.fill = nat_col;
		gen_info_block(fips);
		$(".feature[key=" + current_graph + "] > i").css("font-weight", "bold");
		$('html, body').animate({scrollTop:0}, 'slow');
	}
});

// When click min or max open up that county's info
$("#legend-div").on("click", '.legends', function() {
	unhighlight_all_counties();
	remove_all_hover();
	var fips = parseInt($(this).attr("key"));
	$(".info-block").empty();
	set_current_object(fips);
	highlight_current_county();
	gen_info_block(fips);
	$(".feature[key=" + current_graph + "] > i").css("font-weight", "bold");
	// $('html, body').animate({scrollTop:0}, 'slow');
});


$("#legend-div").on({
    mouseenter: function() {
		var fips = parseInt($(this).attr("key"));
		set_current_object(fips);
		var native_color = current_object.style.fill;
		current_object.__data__.native_color = native_color;
		var class_list = current_object.classList;
		var classes = "path-hovered ";
		for (_class of class_list) {
			if(_class !== "path-hovered") {
				classes += _class;
				classes += " ";
			}
		}
		$(current_object).attr("class", classes);
		if (typeof fips !== 'undefined') {
			color = $(current_object).css("fill");
			$(current_object).css("fill","#76EE00");
		}
    }, mouseleave: function() {
		if (current_object !== current_object) {
			var class_list = current_object.classList;
			var classes = "";
			for (_class of class_list) {
				if(_class !== "path-hovered") {
					classes += _class;
					classes += " ";
				}
			}
			$(current_object).attr("class", classes);
		}
		var fips = current_object.__data__.id;
		var native_color = current_object.__data__.native_color;
		if (typeof fips !== 'undefined') current_object.style.fill = native_color;
    }
}, ".legends");

// Generate new map on info block feature list click
$(".info-block").on("click", ".feature", function(){
	$(".features_list > li").css("font-weight", "normal");
	$(".feature").css("font-weight", "normal");
	var index = $(this).attr('key');
	current_graph = index;
	$(".chosen_feature").css("font-weight", "normal");
	$(".features_list > li[key=" + current_graph + "]").css({"font-weight":"bold","font-style":"normal"});
	$(".feature[key=" + current_graph + "]").css({"font-weight":"bold","font-style":"normal"});
	create_canvas($(this), 1);
});

// Display more info on info block feature hover
$(".info-block").on({
    mouseenter: function () {
    	var key = $(this).attr("key");
    	var fips = current_object.__data__.id;
		var val = county_data[key][fips];
		var cur_percentile = Math.round(get_feature_percentile(key, fips));
		$("#feature-info").html("<span class='rank-width'></span><span class='rank'>" + cur_percentile + "<span>" + number_ender(cur_percentile) + "</span></span><span class='feature-info-text'><b>" + shorten_string(val) + " " + label_info[key][0] + ":</b> " + label_info[key][1] + "</span>");
		var rank_width = String(cur_percentile*10.09) + "px";
		$("#feature-info > .rank-width").css("width",rank_width);
    	$(this).css({"color":"#08519c"});
    }, mouseleave: function () {
    	var key = $(this).attr("key");
    	var fips = current_object.__data__.id;
   		$(this).css({"color":"#000"});
   		var val = county_data[current_graph][fips];
		var cur_percentile = Math.round(get_feature_percentile(current_graph, fips));
   		$("#feature-info").html("<span class='rank-width'></span><span class='rank'>" + cur_percentile + "<span>" + number_ender(cur_percentile) + "</span></span><span class='feature-info-text'><b>" + shorten_string(val) + " " + label_info[current_graph][0] + ":</b> " + label_info[current_graph][1] + "</span>");
   		var rank_width = String(cur_percentile*10.09) + "px";
		$("#feature-info > .rank-width").css("width",rank_width);
    }
}, ".feature");

// On Info Block Category Selection
$(".info-block").on("change", "#category-select", function(){
	$('.feature').show();
	var val = $("option:selected", "#category-select").attr("val");
	var option = $('option:selected', this).attr('mytag');
	$('.feature').not("." + val).hide();
});

// On Feature List Category Selection
$(".feature-box").on("change", "#feature-select", function(){
	$('.feature').show();
	var val = $("option:selected", "#feature-select").attr("val");
	var option = $('option:selected', this).attr('mytag');
	$('.feature').not("." + val).hide();
});

// Close Info Block
$(".info-block").on("click", "#close-info", function(){
	unhighlight_current_county();
	$("#close-info").hide();
	$(".info-block").slideUp();
});

// Toggle Category Block
$("#get-features").on("click",function() {
	var show = $(this).attr("show");
	if (show == "0") {
		$(".feature-box").slideDown();
		$("#feature-select").val("Interesting").trigger('change');
		$(this).attr("show","1");
		$(".svg").css("opacity","0.15");
		$("#county-name").css("opacity","0");
		$(this).text("X");
	} else {
		$(".feature-box").slideUp();
		$(this).attr("show","0");
		$(".svg").css("opacity","1");
		$("#county-name").css("opacity","1");
		$(this).text("Change Map");
	}
});

// Toggle Search
$("#get-search").on("click",function() {
	var show = $(this).attr("show");
	if (show == "0") {
		$("#search-div").show();
		$(this).attr("show","1");
		$(".svg").css("opacity","0.15");
		$("#county-name").css("opacity","0");
		$(this).text("X");
		$("#search-input").focus();
	} else {
		$("#search-div").hide();
		$(this).attr("show","0");
		$(".svg").css("opacity","1");
		$("#search-input").css("opacity","1");
		$(this).text("Search Counties");
	}

});

// Get search results
$("#search-results").on("click", ".search-result", function() {
	unhighlight_current_county()
	$(".info-block").empty();
	var fips = parseInt($(this).attr("data"));
	gen_info_block(fips);
	$("#search-div").hide();
	$(this).attr("show","0");
	$(".svg").css("opacity","1");
	$("#search-input").css("opacity","1");
	$("#get-search").text("Search Counties");

	var all_paths = document.getElementsByTagName("path");
	for(var key in all_paths) {
	    if(all_paths[key].__data__.id == fips){
	    	current_object = all_paths[key];
	    	highlight_current_county();
	    	break;
	    }
	}
});

// Asynchronously get search results
$("#search-input").on('input', function(){
	$("#search-results").empty();
	var input = [$(this).val()];
	if(String(input).length > 0){
		if(input[0].indexOf(' ') !== -1) input = input[0].split(' ');
		var matches = [];
		if(matches.length < 20) {
	    	for(var i = 0; i < counties_list.length; i++) {
	    		var found = true;
	    		for(val of input) {
	      			if(counties_list[i].split("*")[0].toLowerCase().search(val.toLowerCase()) === -1) {
	        			found = false;
	      			}
	    		}
	    		if(found && matches.length < 20) matches.push(i);
	    	}
		}
		for(key of matches) {
			var name = counties_list[key].split("*")[0];
			var fips = counties_list[key].split("*")[1];
			$("#search-results").append("<p class='search-result' data=" + fips + ">" + counties_list[key].split("*")[0] + "</p>");
		}
	}
});

// Bold item on search result mouseover
$("#search-results").on({
    mouseenter: function () {
        $(this).css("font-weight", "bold");
    },
    mouseleave: function () {
        $(this).css("font-weight", "normal");
    }
}, ".search-result");
