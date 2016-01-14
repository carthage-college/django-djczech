$( init );

function init() {
    $('#CarthagePanel').html(
        '<h3>Carthage outstanding checks</h3><div id="CarthageChecks"></div>'
    );
    $('#JohnsonPanel').html(
        '<h3>Johnson Bank information</h3><div id="JohnsonChecks"></div>'
    );
    $("h3").editable(
        'https://www.carthage.edu/jics/business_office/check_reconciliation/check_matching_data.cfm?inline_edit',
        {event: 'dblclick'}
    );
    // dragging and dropping <tr> elements is difficult for some reason.
    // this is part of a work-around dave found
    var c = {};
    var j = {};

  // retrieve open Carthage checks
  $.ajax({
      url: "https://www.carthage.edu/jics/business_office/check_reconciliation/check_matching_data.cfm?c_checks",
      dataType: "json",
      success: function(data) {
          // A Coldfusion thing: Run the response json object through
          // queryToObject to make it easier to work with
          data = queryToObject(data);
          // Build the table manually
          var Carthage_Table = document.createElement("table");
          // Build thead row
          var tbl_head = document.createElement("thead");
          var head_row = tbl_head.insertRow();
          head_row.className = "odd";
          var th = document.createElement('th');
              th.appendChild(document.createTextNode("Check#"));
              $(th).attr( "data-sort", "int" );
              head_row.appendChild(th);
          var th = document.createElement('th');
              th.appendChild(document.createTextNode("Amount"));
              $(th).attr( "data-sort", "float" );
              head_row.appendChild(th);
          var th = document.createElement('th');
              th.appendChild(document.createTextNode("Payee"));
              $(th).attr( "data-sort", "string-ins" );
              head_row.appendChild(th);
          var th = document.createElement('th');
              th.appendChild(document.createTextNode("Issue Date"));
              $(th).attr( "data-sort", "string-ins" );
              head_row.appendChild(th);
          Carthage_Table.appendChild(tbl_head);
          // Build data rows
          var tbl_body = document.createElement("tbody");
          var odd_even = false;
          for (_i = 0, _len = data.length; _i < _len; _i++) {
              row = data[_i];
              var tbl_row = tbl_body.insertRow();
              tbl_row.className = odd_even ? "odd" : "even";
              var cell = tbl_row.insertCell();
                  cell.className = "right";
                  cell.appendChild(document.createTextNode(row.check_number));
              var cell = tbl_row.insertCell();
                  cell.className = "right";
                  cell.appendChild(document.createTextNode((row.amt).formatMoney(2)));
                  $(cell).attr( "data-sort-value", row.amt );
              var cell = tbl_row.insertCell();
                  cell.appendChild(document.createTextNode(row.fullname));
              var cell = tbl_row.insertCell();
                  cell.className = "right";
                  cell.appendChild(document.createTextNode(row.post_date));
              odd_even = !odd_even;
              $(tbl_row).attr( 'id', 'Carthage'+row.check_number );
          }
          // append data rows to tbody
          $(Carthage_Table).append(tbl_body);
          // append tbody to table
          $(Carthage_Table).appendTo( '#CarthageChecks' );
          $("#CarthageChecks").html(Carthage_Table);
          $("#CarthageChecks table").stupidtable();
          // end build table

          // attach drag and drop handlers
          $( "#CarthageChecks tbody tr ").draggable({
              helper: "clone",
              cursor: "move",
              revert: "true",
              containment: '#content',
              stack: '#CarthageChecks table',
              start: function(event, ui) {
                  c.tr = this;
                  c.helper = ui.helper;
              }
          });
          $( "#CarthageChecks tbody tr ").droppable({
              accept: '#JohnsonChecks tr',
              hoverClass: 'hovered',
              drop: function(event, ui) {
                  var target = this;
                  var CarthageNumber = $(this).children('td').eq(0).text();
                  var CarthageAmount = $(this).children('td').eq(1).text();
                  var JohnsonNumber = ui.draggable.children('td').eq(0).text();
                  var JohnsonAmount = ui.draggable.children('td').eq(1).text();
                  var JohnsonSequence = ui.draggable.attr('id')
                  // testing (until I build the real update logic) ...
                  //alert("matching Johnson (" + JohnsonSequence + ") " + JohnsonNumber + "\t" + JohnsonAmount + "\n         with Carthage " + CarthageNumber + "\t" + CarthageAmount);
                   $.ajax({
                      url: "https://www.carthage.edu/jics/business_office/check_reconciliation/check_matching_data.cfm?match_checks",
                      data:  { JohnsonSequence: JohnsonSequence,
                               JohnsonNumber: JohnsonNumber,
                               JohnsonAmount: JohnsonAmount,
                               CarthageNumber: CarthageNumber,
                               CarthageAmount: CarthageAmount},
                      dataType: "json",
                      success: function(data) {
                          if (data) {
                              $(j.tr).remove();
                              $(j.helper).remove();
                              $(target).remove();
                              $('body').css('cursor', 'auto');
                              alert("matched Johnson " + JohnsonNumber + "\t" + JohnsonAmount + "\n         with Carthage " + CarthageNumber + "\t" + CarthageAmount);
                          } else {
                            alert("something went wrong. no match was made.");
                          }
                      }
                  });

              }
          });
      }
  });

  // Retrieve the Johnson check entries
  $.ajax({
      url: "https://www.carthage.edu/jics/business_office/check_reconciliation/check_matching_data.cfm?j_checks",
      dataType: "json",
      success: function(data) {
          // A Coldfusion thing: Run the response json object through
          // queryToObject to make it easier to work with
          data = queryToObject(data);
          // Build the table manually
          var Johnson_Table = document.createElement("table");
          // Build thead row
          var tbl_head = document.createElement("thead");
          var head_row = tbl_head.insertRow();
          head_row.className = "odd";
          var th = document.createElement('th');
              th.appendChild(document.createTextNode("Check#"));
              $(th).attr( "data-sort", "int" );
              head_row.appendChild(th);
          var th = document.createElement('th');
              th.appendChild(document.createTextNode("Amount"));
              $(th).attr( "data-sort", "float" );
              head_row.appendChild(th);
          var th = document.createElement('th');
              th.appendChild(document.createTextNode("Cleared Date"));
              $(th).attr( "data-sort", "string-ins" );
              head_row.appendChild(th);
          var th = document.createElement('th');
              th.appendChild(document.createTextNode("Note"));
              $(th).attr( "data-sort", "string-ins" );
              head_row.appendChild(th);
          Johnson_Table.appendChild(tbl_head);
          // Build data rows
          var tbl_body = document.createElement("tbody");
          var odd_even = false;
          for (_i = 0, _len = data.length; _i < _len; _i++) {
              row = data[_i];
              var tbl_row = tbl_body.insertRow();
              tbl_row.className = odd_even ? "odd" : "even";
              var cell = tbl_row.insertCell();
                  cell.className = "right";
                  cell.appendChild(document.createTextNode(row.check_number));
              var cell = tbl_row.insertCell();
                  cell.className = "right";
                  cell.appendChild(document.createTextNode((row.amt).formatMoney(2)));
                  $(cell).attr( "data-sort-value", row.amt );
              var cell = tbl_row.insertCell();
                  cell.appendChild(document.createTextNode(row.cleared_date));
              var cell = tbl_row.insertCell();
                  note = row.jbaction.trim();
                  if (note == "SuspctDupCKNO") {note = "Duplicate Check #"} else {note = "" };
                  cell.appendChild(document.createTextNode(note));
              odd_even = !odd_even;
              $(tbl_row).attr( 'id', row.jbseqno ).attr( 'title', 'Date imported: '+row.jbpayee+ '\nJB transaction # ' + row.jbaccount ).tooltip();
          }
          // append data rows to tbody
          $(Johnson_Table).append(tbl_body);
          $(Johnson_Table).appendTo( '#JohnsonChecks' );
          $("#JohnsonChecks").html(Johnson_Table);
          $("#JohnsonChecks table").stupidtable();
          // end build table

          // attach drag and drop handlers
          $( "#JohnsonChecks tbody tr ").draggable({
              helper: "clone",
              cursor: "move",
              revert: "true",
              containment: '#content',
              stack: '#JohnsonChecks table',
              start: function(event, ui) {
                  j.tr = this;
                  j.helper = ui.helper;
              }
          });
          $( "#JohnsonChecks tbody tr ").droppable({
              accept: '#CarthageChecks tr',
              hoverClass: 'hovered',
              drop: function(event, ui) {
                  var target = this;
                  var JohnsonNumber = $(this).children('td').eq(0).text();
                  var JohnsonAmount = $(this).children('td').eq(1).text();
                  var JohnsonSequence = $(this).attr('id');
                  var CarthageNumber = ui.draggable.children('td').eq(0).text();
                  var CarthageAmount = ui.draggable.children('td').eq(1).text();
                  // testing (until I build the real update logic) ...
                  //alert("matching Carthage " + CarthageNumber + "\t" + CarthageAmount + "\n          with Johnson " + JohnsonNumber + "\t" + JohnsonAmount);
                   $.ajax({
                      url: "https://www.carthage.edu/jics/business_office/check_reconciliation/check_matching_data.cfm?match_checks",
                      data:  { JohnsonSequence: JohnsonSequence,
                               JohnsonNumber: JohnsonNumber,
                               JohnsonAmount: JohnsonAmount,
                               CarthageNumber: CarthageNumber,
                               CarthageAmount: CarthageAmount},
                      dataType: "json",
                      success: function(data) {
                          if (data) {
                              $(j.tr).remove();
                              $(j.helper).remove();
                              $(target).remove();
                              $('body').css('cursor', 'auto');
                              alert("matched Carthage " + CarthageNumber + "\t" + CarthageAmount + "\n          with Johnson " + JohnsonNumber + "\t" + JohnsonAmount);
                          } else {
                            alert("something went wrong. no match was made.");
                          }
                      }
                  });
              }
          });
          $( "#JohnsonChecks tbody tr td.right").editable('https://www.carthage.edu/jics/business_office/check_reconciliation/check_matching_data.cfm?inline_edit', {event: 'dblclick'})
      }
  });
}

var queryToObject = function(q) {
  var col, i, r, _i, _len, _ref, _ref2, _results;
  _results = [];
  for (i = 0, _ref = q.ROWCOUNT; 0 <= _ref ? i < _ref : i > _ref; 0 <= _ref ? i++ : i--) {
    r = {};
    _ref2 = q.COLUMNS;
    for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
      col = _ref2[_i];
      r[col.toLowerCase()] = q.DATA[col][i];
    }
    _results.push(r);
  }
  return _results;
};

Number.prototype.formatMoney = function(c, d, t){
    var n = this,
        c = isNaN(c = Math.abs(c)) ? 2 : c,
        d = d == undefined ? "." : d,
        t = t == undefined ? "," : t,
        s = n < 0 ? "-" : "$",
        i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "",
        j = (j = i.length) > 3 ? j % 3 : 0;
    return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
};
