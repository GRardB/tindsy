$(function() {

  var spinnerOptions = {
    lines: 7,
    length: 0,
    width: 5,
    radius: 50,
    corners: 1,
    rotate: 0,
    direction: 1,
    color: '#000',
    speed: 1,
    trail: 50,
    shadow: false,
    hwaccel: false,
    className: 'spinner',
    zIndex: 2e9,
  };

  var body = document.getElementsByTagName('body')[0];
  var spinner = new Spinner(spinnerOptions);

  var $body = $('body');
  var $listing = $('#listing');
  var $listingTitle = $('#listing-title');
  var $listingImage = $('#listing-image');
  var $numFavorites = $('#num-favorites');
  var $dislikeButton = $('#dislike-button');
  var $likeButton = $('#like-button');
  var listingId = null;

  var getListing = function() {
    $likeButton.attr('disabled', true);
    $dislikeButton.attr('disabled', true);
    $body.addClass('loading');
    $listing.fadeOut();
    spinner.spin(body);

    $.getJSON('/get_listing', function(data) {

      listingId = data['listing_id'];
      var listingImage = new Image();
      listingImage.src = data['listing_image'];

      listingImage.onload = function() {
        spinner.stop();
        $body.removeClass('loading');

        $listing.fadeIn();
        $likeButton.attr('disabled', false);
        $dislikeButton.attr('disabled', false);

        var listingTitle = data['listing_title'];
        if (listingTitle.length >= 50) {
          listingTitle = listingTitle.substring(0, 45) + '…';
          $listingTitle.attr('title', data['listing_title']);
        }

        $listingTitle.text(listingTitle);
        $listingImage.attr('src', data['listing_image']);

        var numFavs = data['num_favorites'];
        var fav = parseInt(numFavs) === 1 ? 'favorite' : 'favorites';
        $numFavorites.text(numFavs + ' ' + fav);
      };
    });
  };

  $dislikeButton.on('click', getListing);

  $likeButton.on('click', function() {
    if (listingId !== null) {
      $.post('/favorite', {
        listing_id: listingId
      })

      getListing();
    }
  });

  getListing();
});
