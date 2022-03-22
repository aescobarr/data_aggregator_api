$(document).ready(function() {
    var map = L.map('map').setView([51.505, -0.09], 1);
    var data_urls = [];
	var markers = [];
	var page_size = 100;
	var base_data_url = '/api/observation/?ordering=-observation_time'

	var tiles = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ' +
			'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		id: 'mapbox/streets-v11',
		tileSize: 512,
		zoomOffset: -1
	}).addTo(map);

	var refresh_data_urls = function(page_size,total_records){
	    data_urls = [];
	    $('#pages').html('');
	    var num_pages = Math.ceil(total_records/page_size);
	    for(var i = 0; i < num_pages; i++){
	        if(i==0){
	            data_urls.push(base_data_url + '&limit=' + page_size);
	        }else{
	            data_urls.push(base_data_url + '&limit=' + page_size + '&offset=' +  page_size * i);
	        }
	    }
	    for(var i = 0; i < data_urls.length; i++){
	        $('#pages').append('<li><button class="page_load" data-url-idx="' + i + '">' + (i+1) + '</button></li>');
	    }
	}

	var clear_markers = function(){
	    for(var i = 0; i < markers.length; i++){
            var m = markers[i];
            map.removeLayer(m);
        }
	}

	var load_data = function(url){
            $.ajax({
            url: url,
            type: "GET",
            dataType: "json",
            success: function(data) {
                refresh_data_urls(page_size,data.count);
                clear_markers();
                for(var i = 0; i < data.results.length; i++){
                    var d = data.results[i];
                    if(d.location != null){
                        var marker = L.marker([d.location.lat, d.location.long]).addTo(map);
                        markers.push(marker);
                        marker.bindPopup('<b><i>' + d.species + '</i></b><br /><a href="' + d.original_url + '" target="_blank"><img src="' + d.picture_url + '" width="200" height="200"></a><p>' + d.observation_time + '</p>');
                    }
                }
                var points = data.results.map(function(d){
                    if(d.location != null){
                        return L.latLng( d.location.lat, d.location.long );
                    }
                });
                var bounds = L.latLngBounds(points);
                map.fitBounds(bounds);
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log(errorThrown);
            }
        });
	}

	$('body').on('click', 'button.page_load', function() {
	    var index = $(this).data("url-idx");
	    var url = data_urls[index];
	    load_data(url);
    });

    load_data(base_data_url + '&limit=' + page_size);

});
