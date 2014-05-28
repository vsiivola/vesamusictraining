/*jslint browser: true*/
/*globals Translator, lang, $*/

var et = new Translator("exercisepage", lang);

function Choice(type, image, ogg, mp3, text) {
    "use strict";
    this.type = type;
    this.image = image;
    this.ogg = ogg;
    this.mp3 = mp3;
    this.text = text;

    this.build_dom = function () {
        var empty_stave_td,
            span_icon,
            span_qmark;

        if (this.type === "image_question" || this.type === "image_response") {
            this.dom = $('<td align="center" width="260">' +
                         '<img style="position:relative" src="' + this.image + '"/>' +
                         '<br>' + this.text +
                         '</br></td>');
            return;
        }

        empty_stave_td = $(
            '<td align="center" width="260">' +
                '<img src="/static/generated_assets/images/empty_stave.png" ' +
                'class="empty_image" style="position:relative"/>' +
                '</td>');
        span_icon = $('<span class="span_icon" style="position:relative" />');
        span_qmark = $('<span class="qmark altaudio" style="position:relative">?</span>');

        if (this.type === "audio_question") {
            span_qmark.css("left", -60 + "px");
            span_qmark.css("top", -15 + "px");
            span_icon.css("top", -55 + "px");
            span_icon.css("left", -65 + "px");
            this.dom = empty_stave_td;
            this.dom.append(span_qmark);
            this.dom.append(span_icon);
        } else {
            span_qmark.css("left", -120 + "px");
            span_qmark.css("top", -1 + "px");
            span_icon.css("top", -40 + "px");
            span_icon.css("left", -210 + "px");
            this.dom = $('<td align="center" width="260"><table class="buttontable"><tr class="empty_stave"></tr><tr><td align="center"><button class="ui-button-text">' + et.tp("Play") + '</button></td></tr></table>');
            $("tr.empty_stave", this.dom).append(empty_stave_td);
            $("tr.empty_stave", this.dom).append(span_qmark);
            $("tr.empty_stave", this.dom).append(span_icon);
        }
    };

    this.play_audio = function () {
        var audioElement = document.createElement('audio'),
            source = document.createElement('source');

        if (audioElement.canPlayType('audio/ogg;')) {
            source.type = 'audio/ogg';
            source.src = this.ogg;
        } else {
            source.type = 'audio/mpeg';
            source.src = this.mp3;
        }
        audioElement.appendChild(source);
        audioElement.play();
    };

    this.initial_overlays = function () {
        if (this.type !== "audio_question"
                && this.type !== "audio_response") {
            return;
        }

        $(".empty_image", this.dom).delay(500).animate({opacity: 0.4}, 3000);
        $("span.qmark", this.dom).delay(200).animate({opacity: 1.0}, 3000);

        if (this.type === "audio_question") {
            $("span.span_icon", this.dom).addClass("ui-icon ui-icon-circle-triangle-e");
            var overlay_context = this;
            this.dom.click(function () {
                overlay_context.play_audio();
            });
        }
    };

    this.display_result = function (myex, parent, correct) {
        var span_icon = $("span.span_icon", this.dom),
            color;

        if (correct) {
            span_icon.addClass("ui-icon ui-icon-circle-check checkremove");
            color = "rgb(100,200,100)";
        } else {
            span_icon.addClass("ui-icon ui-icon-circle-close checkremove");
            color = "rgb(200,100,100)";
            if (this.type === "image_response") {
                this.play_audio();
            }
        }

        if (this.type === "audio_response") {
            $("img", this.dom).attr("src", this.image);
            $(".empty_image", this.dom).animate({opacity: 0.8}, 3000);
        }
        $("span.qmark", this.dom).animate({opacity: 1.0}, 3000);
        span_icon.animate({opacity: 1.0}, 3000);
        $("img", this.dom).css("background-color", color);
        if (correct) {
            if (myex.num_clicks === 1) {
                myex.mainWindow.correct_clicks += 1;
            }
            myex.mainWindow.exercise_index += 1;
            myex.clear_statics(function () {
                myex.mainWindow.show.apply(myex.mainWindow);
            });
        }
    };

    this.bind_events = function (ethis) {
        var event_context = this,
            clickable = null;
        if (this.type === "audio_response") {
            $("button", this.dom).click(function () {
                event_context.play_audio();
            });
            clickable = $(".empty_stave, .altaudio", this.dom);
        } else {
            clickable = this.dom;
        }

        clickable.one("click", function () {
            $(".empty_stave, .altaudio", event_context).off("click");
            ethis.num_clicks += 1;
            //$("div#debug").append("cidx " + athis.idstring + ", img" + athis.image);
            $.get('/exercise/' + ethis.mainWindow.course_name + '/verify/',
                {
                    "exercise_index" : ethis.mainWindow.exercise_index,
                    "chosen" : event_context.type === "audio_response" ?
                            event_context.ogg : event_context.image,
                    "num_exercises" : ethis.mainWindow.num_exercises
                },
                function (response) {
                    var respi = JSON.parse(response);
                    event_context.image = respi.image;
                    event_context.mp3 = respi.mp3;
                    event_context.ogg = respi.ogg;
                    event_context.text = respi.text;
                    //$("div#debug").append("cidx " + athis.idstring + ", img" + athis.image);
                    event_context.display_result(ethis, event_context, respi.correct);
                });
        });
    };
}

function ExerciseScreen(mainWindow) {
    "use strict";
    this.mainWindow = mainWindow;

    this.render_full = function (response) {
        $("div#main").html("");
        var escreen_context = this,
            i,
            cur_choice;

        /* Fetch and build question before
           updating the display */
        this.question = new Choice(
            response.question_type + "_question",
            response.question_image,
            response.question_ogg,
            response.question_mp3,
            response.text
        );
        this.question.build_dom();

        /* Fetch and build the responses before
           updating the display */
        this.choices = [];
        for (i = 0; i < response.num_alt; i += 1) {
            if (response.question_type === "audio") {
                cur_choice = new Choice(
                    "image_response",
                    response["alt" + i + "_image"],
                    null,
                    null,
                    response["alt" + i + "_text"]
                );
            } else {
                cur_choice = new Choice(
                    "audio_response",
                    null,
                    response["alt" + i + "_ogg"],
                    response["alt" + i + "_mp3"],
                    response["alt" + i + "_text"]
                );
            }
            cur_choice.build_dom();

            this.choices[i] = cur_choice;
        }

        this.num_clicks = 0;

        $("div#main").slideUp("slow", function () {
            escreen_context.real_render(response);
        });
    };

    this.real_render = function (response) {
        this.mainWindow.num_exercises = response.num_exercises;
        $("#maintitle").html(
            et.tp("Music Training") + " | " +
                this.mainWindow.course_name
        );
        var tstring = (
            '<h2 class="ui-widget-header ui-corner-all" style="text-align:center;">' +
                response.name +
                " (" + (this.mainWindow.exercise_index + 1) +
                "/" + (this.mainWindow.num_exercises)
                + ')</h2>\
<div class="ui-widget-content" id="test_images">\
 <table width="100%" cellpadding="20%">\
  <tr id="question"></tr></table>\
 <table width="100%" class="alttable">\
  <tr id="alttr"></tr>\
 </table>\
</div>'),
            render_context,
            i,
            cur_choice;

        $("div#main").html(tstring);
        $("tr#question").append(this.question.dom);
        this.question.initial_overlays(); // FIXME, ui glitches

        render_context = this;
        $("div#main").slideDown(function () {
            render_context.question.play_audio();
            for (i = 0; i < response.num_alt; i += 1) {
                cur_choice = render_context.choices[i];
                $("tr#alttr").append(cur_choice.dom);
                cur_choice.initial_overlays();
                cur_choice.bind_events(render_context);
            }
        });
    };

    this.get_server_info = function (course_name, exercise_index) {
        var that = this; //preserve context for callback
        //$("div#debug").append(" getting exnum " + exercise_index)
        $.get(
            '/exercise/' + course_name + '/lecture/',
            {"exercise_index": exercise_index},
            function (response) {that.res.apply(that, arguments); }
        );
    };

    this.res = function (response) {
        this.render_full(JSON.parse(response));
    };

    this.clear_statics = function (callback) {
        $("span").removeClass("ui-icon ui-icon-circle-triangle-e ui-icon-circle-check ui-icon-circle-close checkremove");
        $("div.overlay").css("opacity", "0.0");
        $("span.qmark").css("opacity", "0.0");
        callback();
    };
}
