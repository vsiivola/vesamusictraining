et = new Translator("exercisepage", lang);

function Choice(type, image, ogg, mp3, text) {
    this.type = type;
    this.image = image;
    this.ogg = ogg;
    this.mp3 = mp3;
    this.text = text;

    this.build_dom = function () {
        if (this.type == "image_question" || this.type == "image_response") {
            this.dom = $('<td align="center" width="260"><img src="' + this.image + '"></img><br>' + this.text +'</td>');
            return;
        }

        var empty_stave_td = $('<td align="center" width="260"><img src="/static/generated_assets/images/empty_stave.png" class="empty_image"></img></td>');

        if (this.type == "audio_question") {
            this.dom = empty_stave_td;
            return;
        }

        this.dom = $('<td align="center" width="260"><table class="buttontable"><tr class="empty_stave"></tr><tr><td align="center"><button class="ui-button-text">'+et.tp("Play")+'</button></td></tr></table>');
        $("tr.empty_stave", this.dom).append(empty_stave_td);
    }

    this.play_audio = function () {
        var audioElement = document.createElement('audio');
        var source= document.createElement('source');
        
        if (audioElement.canPlayType('audio/ogg;')) {
            source.type= 'audio/ogg';
            source.src= this.ogg;
        } else {
            source.type= 'audio/mpeg';
            source.src= this.mp3;
        }
        audioElement.appendChild(source);
        audioElement.play()
    }

    this.initial_overlays = function() {
        var img = $("img", this.dom);
        var span_icon = $('<span class="span_icon"></span>');
        var aathis = this;

        span_icon.css("top", img.offset().top + "px");
        span_icon.css("left", img.offset().left - 2 + "px");
        aathis.dom.append(span_icon);
        
        if (aathis.type == "audio_question" || aathis.type == "audio_response") {
            
            var span_qmark = $('<span class="qmark altaudio">?</span>');
            span_qmark.css("top", img.offset().top + "px");
            span_qmark.css("left", img.offset().left + 60 + "px");
            aathis.dom.append(span_qmark)
            $(".empty_image", aathis).delay( 500).animate({opacity:0.2}, 3000);
            span_qmark.delay( 500 ).animate({opacity:1.0}, 3000);
            
            if (aathis.type == "audio_question") {
                setTimeout( function () {
                    span_icon.addClass("ui-icon ui-icon-circle-triangle-e")
                    }, 1000);
                uthis=aathis;
                aathis.dom.click(function () {
                    uthis.play_audio();
                });
            }
        }
    }

    this.display_result = function(myex, parent, correct) {
        var span_icon = $("span.span_icon", this.dom);
        var img = $("img", this.dom);
        
        if (correct) {
            span_icon.addClass("ui-icon ui-icon-circle-check checkremove");
            color = "rgb(100,200,100)";
        } else {
            span_icon.addClass("ui-icon ui-icon-circle-close checkremove");
            color = "rgb(200,100,100)";
            if (this.type=="image_response") {
                this.play_audio()
            }
        }

        if (this.type=="audio_response") {
            img.attr("src", this.image);
            $(".empty_image", this.dom).animate({opacity:0.8}, 3000);

            var mydom = this.dom;
            var topobj = this;
            img.load(function() {
                var span_qmark = $("span.qmark", mydom);
                span_icon.css("top", $(this).offset().top + "px");
                span_icon.css("left", $(this).offset().left - 2 + "px");
                span_qmark.css("top", $(this).offset().top + "px");
                span_qmark.css("left", $(this).offset().left + 60 + "px");
                span_qmark.animate({opacity:0.0}, 3000);
                
                topobj.do_overlay(myex, parent, mydom, img, color, span_icon, correct);
            });
        } else {
            this.do_overlay(myex, parent, this.dom, img, color, span_icon, correct)
        }
    }

    this.do_overlay = function(ex, parenta, mydom, img, color, span_icon, correct) {
        overlay = $('<div class="overlay"></div>')
        overlay.width(img.css("width"));
        overlay.height(img.css("height"));
        overlay.css("top", img.offset().top + "px");
        overlay.css("left", img.offset().left + "px");
        overlay.css("background-color", color);
        overlay.css("opacity", "0.7");
        mydom.append(overlay)
        span_icon.animate({opacity:1.0}, 3000);

        //$("div#debug").append("exnum " + ex.mainWindow.exercise_index)
        parenta.dom.ready( function() {
            $("div", parenta.dom).animate({opacity:0.2}, {duration: 1500, easing: 'linear', complete: function () {
                if (correct) {
                    if (ex.num_clicks==1) {
                        ex.mainWindow.correct_clicks += 1;
                    }
                    ex.mainWindow.exercise_index += 1;
                    ex.clear_statics(function () {
                        ex.mainWindow.show.apply(ex.mainWindow);
                    });
                    return;
                }
            }});
        });
        
    }

    this.bind_events = function (ethis) {
        var athis = this;
        var clickable = null;
        if (this.type == "audio_response") {
            $("button", this.dom).click(function () {athis.play_audio()}); 
            clickable = $(".empty_stave, .altaudio", this.dom);
        } else {
            clickable = this.dom;
        }
        
        clickable.one("click", function () {
            $(".empty_stave, .altaudio", athis).off("click");
            ethis.num_clicks+=1;
            //$("div#debug").append("cidx " + athis.idstring + ", img" + athis.image);
            $.get('/exercise/'+ethis.mainWindow.course_name+'/verify/', 
                  {
                      "exercise_index" : ethis.mainWindow.exercise_index, 
                      "chosen" : athis.type=="audio_response" ? athis.ogg : athis.image,
                      "num_exercises" : ethis.mainWindow.num_exercises},
                  function(response) {
                      var infoarray;
                      var respi = JSON.parse(response)
                      athis.image=respi["image"];
                      athis.mp3=respi["mp3"];
                      athis.ogg=respi["ogg"];
                      athis.text=respi["text"]
                      //$("div#debug").append("cidx " + athis.idstring + ", img" + athis.image);
                      athis.display_result(ethis, athis, respi["correct"]);
                  });
        });

    }

}

function ExerciseScreen(mainWindow) {
    this.mainWindow = mainWindow

    this.render_full = function(response) {
        var that = this;
        var thatarg = arguments;
        $("div#main").slideUp("slow", function () {that.real_render.apply(that, thatarg);});
    }

    this.real_render = function(response) {
        this.mainWindow.num_exercises = response.num_exercises
        $("#maintitle").html(et.tp("Music Training") + " | " + this.mainWindow.course_name);
        var tstring = ( 
            '<h2 class="ui-widget-header ui-corner-all" style="text-align:center;">'+response.name
                + " ("+(this.mainWindow.exercise_index+1)+"/" + (this.mainWindow.num_exercises) 
                + ')</h2>\
<div class="ui-widget-content" id="test_images">\
 <table width="100%" cellpadding="20%">\
  <tr id="question"></tr></table>\
 <table width="100%" class="alttable">\
  <tr id="alttr"></tr>\
 </table>\
</div>');
        $("div#main").html(tstring);

        var q = new Choice(response.question_type+"_question", response.question_image, 
                           response.question_ogg, response.question_mp3, response.text);
        q.build_dom();
        $("tr#question").append(q.dom);

        var ethis = this;
        this.choices = []
        for (var i=0; i<response.num_alt; i++) {
            if (response.question_type == "audio") {
                var c = new Choice("image_response", response["alt"+i+"_image"], null, null, response["alt"+i+"_text"]);
            } else {
                var c = new Choice("audio_response", null, response["alt"+i+"_ogg"], response["alt"+i+"_mp3"], response["alt"+i+"_text"]);
            }
            c.build_dom();
            $("tr#alttr").append(c.dom);
            this.choices[i] = c;
        }

        this.num_clicks=0;
        $("div#main").slideDown(function() { 
            q.play_audio();
            q.initial_overlays();
            for (var i=0; i<response.num_alt; i++) {
                ethis.choices[i].initial_overlays();
                ethis.choices[i].bind_events(ethis);
            }
        });
    }

    this.get_server_info = function(course_name, exercise_index) {
        var that = this; //preserve context for callback
        //$("div#debug").append(" getting exnum " + exercise_index)
        $.get(
            '/exercise/'+course_name+'/lecture/', 
            {"exercise_index": exercise_index}, 
            function(response) {that.res.apply(that, arguments);})
    }

    this.res = function(response) {
        this.render_full(JSON.parse(response));
    }

    this.clear_statics = function (callback) {
        $("span").removeClass("ui-icon ui-icon-circle-triangle-e ui-icon-circle-check ui-icon-circle-close checkremove");
        $("div.overlay").css("opacity", "0.0")
        $("span.qmark").css("opacity", "0.0")
        callback();
    }
}
