$(function() {
  'use strict';
  $('input:radio').on('change', function(e) {
    var $radio = $(e.target);
    var colNum = $radio.parent('td').data('column');
    $('td[data-column=' + colNum + ']').each(function() {
      $(this).children('input:radio').prop('checked', false);
    });
    $radio.prop('checked', true);
  });
});
