$(function() {
  'use strict';

  // Do not allow multiple radio buttons to be checked in a given column
  // The same condition for rows is automatically satisfied by the browser
  // Uses special data-column attribute on each <td> to find cells in the same
  // column
  // This handler also always clicking anywhere within the <td> to act as a
  // click on the contained radio input
  $('.poll td').on('click', function(e) {
    if ($(e.target).is('input:radio')) {
        var $radio = $(e.target);
    } else {
        var $radio = $(e.target).children('input:radio');
    }
    var colNum = $radio.parent('td').data('column');
    $('td[data-column=' + colNum + '] input:radio').prop('checked', false);
    $radio.prop('checked', true);
  });
});
