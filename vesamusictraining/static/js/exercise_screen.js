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
            span_qmark;

        if (this.type === "image_response") {
            this.dom = $('<div class="text-center col-xs-4 col-lecture">' +
                         '<img class="image_answer" src="' + this.image + '"/>' +
                         '<p><h3>' + this.text + '</h3></p></div>');
            return;
        }

        if (this.type === "image_question") {
            this.dom = $('<div class="text-center">' +
                         '<img class="image_answer" src="' + this.image + '"/>' +
                         '<p><h3>' + this.text + '</h3></p></div>');
            return;
        }

        empty_stave_td = $(
            '<div class="text-center"><img src="/static/generated_assets/images/empty_stave.svg" ' +
                'class="empty_image image_question" /></div>');
        span_qmark = $('<span class="qmark altaudio">?</span>');
        empty_stave_td.append(span_qmark);

        if (this.type === "audio_question") {
            this.dom = empty_stave_td;
            return;
        }

        this.dom = $('<div class="text-center col-xs-4 col-lecture">');
        this.dom.append(empty_stave_td);
        this.dom.append( $('<div><button class="btn btn-lg btn-primary btn-block">' + et.tp("Play") + '</button></div>'));

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
            var overlay_context = this;
            this.dom.click(function () {
                overlay_context.play_audio();
            });
        }
    };

    this.display_result = function (myex, correct) {
        var color;

        if (correct) {
            color = "rgb(100,200,100)";
        } else {
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
                    event_context.display_result(ethis, respi.correct);
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
            '<h2>' +
                response.name +
                " (" + (this.mainWindow.exercise_index + 1) +
                "/" + (this.mainWindow.num_exercises)
                + ')</h2><div class="text-center" id="test_images"><div id="question"/><div class="clearfix"/><div class="alttable row text-center" id="alttr"/></div>'),
            render_context,
            i,
            cur_choice;

        $("div#main").html(tstring);
        $("div#question").append(this.question.dom);
        this.question.initial_overlays(); // FIXME, ui glitches

        render_context = this;
        $("div#main").slideDown(function () {
            render_context.question.play_audio();
            for (i = 0; i < response.num_alt; i += 1) {
                cur_choice = render_context.choices[i];
                $("div#alttr").append(cur_choice.dom);
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
        //$("span").removeClass("ui-icon ui-icon-circle-triangle-e ui-icon-circle-check ui-icon-circle-close checkremove");
        $("div.overlay").css("opacity", "0.0");
        $("span.qmark").css("opacity", "0.0");
        callback();
    };
}
