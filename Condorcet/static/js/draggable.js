(function () {
	'use strict';

	var byId = function (id) { return document.getElementById(id); },

        loadScripts = function (desc, callback) {
            var deps = [], key, idx = 0;

            for (key in desc) {
                deps.push(key);
            }

            (function _next() {
                var pid,
                    name = deps[idx],
                    script = document.createElement('script');

                script.type = 'text/javascript';
                script.src = desc[deps[idx]];

                pid = setInterval(function () {
                    if (window[name]) {
                        clearTimeout(pid);

                        deps[idx++] = window[name];

                        if (deps[idx]) {
                            _next();
                        } else {
                            callback.apply(null, deps);
                        }
                    }
                }, 30);

                document.getElementsByTagName('head')[0].appendChild(script);
            })()
        },

        console = window.console;

    byId("draggablePoll").style.display = "block" ;
    byId("voteButton").disabled = true ;
    // Nasty hack to get same size boxes
    byId("ranking").style.height = byId("pool").clientHeight + 'px';
    var numChoices = Math.sqrt(byId("radioPoll").length-1);

	if (!console.log) {
		console.log = function () {
			alert([].join.apply(arguments, ' '));
		};
	}

    // Reshuffle candidate list
    var pool = byId('pool');
    for (var i = pool.children.length; i >= 0; i--) {
        pool.appendChild(pool.children[Math.random() * i | 0]);
    }

    // Build ranking sortable
	Sortable.create(byId('ranking'), {
        group: {name: "words",
                pull: false,
                put: true},
		animation: 150,
		store: {
			get: function (sortable) {
				var order = localStorage.getItem(sortable.options.group);
				return order ? order.split('|') : [];
			},
			set: function (sortable) {
				var order = sortable.toArray();
				localStorage.setItem(sortable.options.group, order.join('|'));
			}
		},
		onAdd: function (evt){
            if (this.el.children.length==numChoices) {
                var radioPoll = byId("radioPoll");
                for (var i = 0; i < numChoices; i++ ){
                    var myChoice = this.el.children[i].textContent;
                    // console.log('test:', myChoice );
                    for (var radioi = 0; radioi < numChoices; radioi++){
                        // console.log(radioPoll[radioi+i*numChoices]);
                        if (radioPoll[radioi+i*numChoices].value==myChoice){
                            radioPoll[radioi+i*numChoices].checked = true;
                            continue;
                        }
                    }
                }
                byId("voteButton").disabled = false ;
            };
        },
        // onUpdate: function (evt){ console.log('onUpdate.ranking:', [evt, evt.from]); },
        // onRemove: function (evt){ console.log('onRemove.ranking:', [evt, evt.from]); },
        // onStart:function(evt){ console.log('onStart.ranking:', [evt, evt.from]);},
        // onSort:function(evt){ console.log('onStart.ranking:', [evt, evt.from]);},
        // onEnd: function(evt){ console.log('onEnd.ranking:', [evt, evt.from]);}
	});

    // Build candidate pool sortable
	Sortable.create(byId('pool'), {
        group: {name: "words",
                pull: true,
                put: false},
		// group: "words",
		animation: 150,
		// onAdd: function (evt){ console.log('onAdd.pool:', evt.item); },
		// onUpdate: function (evt){ console.log('onUpdate.pool:', evt.item); },
		// onRemove: function (evt){ console.log('onRemove.pool:', evt.item); },
		// onStart:function(evt){ console.log('onStart.pool:', evt.item);},
		// onEnd: function(evt){
            // console.log('onEnd.pool:', evt);
            // // if (evt.from.children.length==0) {
                // // console.log('onEnd.pool: empty!');
                // // byID('ranking').style.backgroundColor = '#008000' ;
            // // };
        // }
	});

})();



