/**
 * Injects the Data Protection notice onto sites
 * For guidance on using: https://www.ebi.ac.uk/style-lab/websites/patterns/banner-data-protection.html
 */
function ebiFrameworkCreateDataProtectionBanner() {
  var banner = document.createElement('div');
  var wrapper = document.createElement('div');
  var inner = document.createElement('div');

  // don't accidently create two banners
  if (document.getElementById("data-protection-banner") != null) {
    document.getElementById("data-protection-banner").remove();
  }

  banner.id = "data-protection-banner";
  banner.className = "data-protection-banner";
  banner.style.cssText = "position: fixed; background: #111; width: 100%; padding: .75rem 1%; left: 0; bottom: 0; color: #eee; z-index: 10;";
  wrapper.className = "row";
  wrapper.innerHTML = "" +
    "<div class='columns medium-8 large-9 white-color'>" +
    dataProtectionSettings.message +
    "</div>" +
    "<div class='columns medium-4 large-3 text-right white-color'><a id='data-protection-agree' class=''>I agree, dismiss this banner</a></div>" +
    "";

  document.body.appendChild(banner);
  banner.appendChild(wrapper);

  ebiFrameworkTrackDataProtectionBanner();

  openDataProtectionBanner();
}

/**
 * Log acceptance of banner, if GA is set and using EBIFoundationExtend
 *
 */
function ebiFrameworkTrackDataProtectionBanner() {
  var bannerTrackingEventLoaded = 0; // has the tracking coad loaded?
  if ((typeof analyticsTrackInteraction == 'function') && (typeof jQuery == 'function')) {
    if (jQuery("body").hasClass("google-analytics-loaded")) {
      bannerTrackingEventLoaded = 1;
      jQuery("body.google-analytics-loaded .data-protection-banner a").on('mousedown', function(e) {
        analyticsTrackInteraction(e.target,'Data protection banner');
      });
    } else {
      bannerTrackingEventLoaded = ebiFrameworkRetryTrackDataProtectionBanner(bannerTrackingEventLoaded);
    }
  } else {
    bannerTrackingEventLoaded = ebiFrameworkRetryTrackDataProtectionBanner(bannerTrackingEventLoaded);
  }
}

/**
 * Give a second for banner checking if GA was slow to load
 *
 */
function ebiFrameworkRetryTrackDataProtectionBanner(bannerTrackingEventLoaded) {
  bannerTrackingEventLoaded --;
  if (bannerTrackingEventLoaded > -3) { // try up to 3 fails
    setTimeout(ebiFrameworkTrackDataProtectionBanner, 900);
  }
  return bannerTrackingEventLoaded;
}

/**
 * Shows the data protection banner on screen.
 */
function openDataProtectionBanner() {
  var height = document.getElementById('data-protection-banner').offsetHeight || 0;
  document.getElementById('data-protection-banner').style.display = 'block';
  document.body.style.paddingBottom = height+'px';

  document.getElementById('data-protection-agree').onclick = function() {
    closeDataProtectionBanner();
    return false;
  };
}

/**
 * Hides the data protection banner from the screen.
 */
function closeDataProtectionBanner() {
  var height = document.getElementById('data-protection-banner').offsetHeight;
  document.getElementById('data-protection-banner').style.display = 'none';
  document.body.style.paddingBottom = '0';
  ebiFrameworkSetCookie(dataProtectionSettings.cookieName, 'true', 90);
}

function ebiFrameworkSetCookie(c_name, value, exdays) {
  var exdate = new Date();
  var c_value;
  exdate.setDate(exdate.getDate() + exdays);
  // c_value = escape(value) + ((exdays===null) ? "" : ";expires=" + exdate.toUTCString()) + ";domain=.ebi.ac.uk;path=/";
  // document.cookie = c_name + "=" + c_value;
  c_value = escape(value) + ((exdays===null) ? "" : ";expires=" + exdate.toUTCString()) + ";domain=" + document.domain + ";path=/";
  document.cookie = c_name + "=" + c_value;
}

function ebiFrameworkGetCookie(c_name) {
  var i, x, y, ARRcookies=document.cookie.split(";");
  for (i=0; i<ARRcookies.length; i++) {
    x = ARRcookies[i].substr(0, ARRcookies[i].indexOf("="));
    y = ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
    x = x.replace(/^\s+|\s+$/g,"");
    if (x===c_name) {
      return unescape(y);
    }
  }
}

var dataProtectionSettings =  new Object();

/**
 * The main 'brain' of the EBI Data Protection banner.
 * Further documentation at https://www.ebi.ac.uk/style-lab/websites/patterns/banner-data-protection.html
 * @param {string} [targetedFrameworkVersion=generic] targeted Framework version; options: 1.1, 1.2, 1.3, compliance, other
 */
function ebiFrameworkRunDataProtectionBanner(targetedFrameworkVersion) {
  try {

    if (typeof newDataProtectionNotificationBanner !== "undefined") {
      targetedFrameworkVersion = newDataProtectionNotificationBanner.src.split('legacyRequest=')[1] || 'generic';
    }

    var compatibilityStyles = document.createElement('style');
    compatibilityStyles.innerHTML = `
      #cookie-banner {
        display: none;
      }
      .data-protection-banner {
        box-sizing: border-box;
      }
      .data-protection-banner a,
      .data-protection-banner a:hover {
        cursor: pointer;
        color: #fff;
        border-bottom-width: 1px;
        border-bottom-style: dotted;
        border-bottom-color: inherit;
        text-decoration: none;
      }
      .data-protection-banner .medium-8 {
        width: 75%; margin-left: 1%; float: left;
      }
      .data-protection-banner .medium-4 {
        width: 23%; margin-right: 1%; float: right; text-align: right;
      }
    `;

    // remove any old style cookie banner
    switch (targetedFrameworkVersion) {
      case '1.1':
      case '1.2':
        if (document.getElementById("cookie-banner") != null) {
          document.getElementById("cookie-banner").remove();
        }
        document.body.style.paddingBottom = 0;
        break;
      case '1.3':
        // cookie banner really shouldn't be here, but just in case
        if (document.getElementById("cookie-banner") != null) {
          document.getElementById("cookie-banner").remove();
        }
        break;
      case 'compliance':
        if (document.getElementById("cookie-banner") != null) {
          document.getElementById("cookie-banner").remove();
        }
        document.body.style.paddingTop = 0;
        document.body.appendChild(compatibilityStyles);
        break;
      case 'other':
        // If you're not using any fomally supported framework, we'll do our best to help out
        document.body.appendChild(compatibilityStyles);
        break;
      default:
        console.warn('You should specify the targeted FrameworkVersion (allowed values: 1.1, 1.2, 1.3, compliance, other). You sent: ' + targetedFrameworkVersion);
    }

    // Default global values
    dataProtectionSettings.message = 'This website requires cookies, and the limited processing of your personal data in order to function. By using the site you are agreeing to this as outlined in our <a target="_blank" href="https://www.ebi.ac.uk/data-protection/privacy-notice/embl-ebi-public-website">Privacy Notice</a> and <a target="_blank" href="https://www.ebi.ac.uk/about/terms-of-use">Terms of Use</a>.';
    dataProtectionSettings.serviceId = 'embl-ebi-public-website'; // use the URL stub from your DP record at http://content.ebi.ac.uk/list-data-protection-records
    dataProtectionSettings.dataProtectionVersion = '1.0';

    // If there's a div#data-protection-message-configuration, override defaults
    var divDataProtectionBanner = document.getElementById('data-protection-message-configuration');
    if (divDataProtectionBanner !== null) {
      if (typeof divDataProtectionBanner.dataset.message !== "undefined") {
        dataProtectionSettings.message = divDataProtectionBanner.dataset.message;
      }
      if (typeof divDataProtectionBanner.dataset.serviceId !== "undefined") {
        dataProtectionSettings.serviceId = divDataProtectionBanner.dataset.serviceId;
      }
      if (typeof divDataProtectionBanner.dataset.dataProtectionVersion !== "undefined") {
        dataProtectionSettings.dataProtectionVersion = divDataProtectionBanner.dataset.dataProtectionVersion;
      }
    }

    dataProtectionSettings.cookieName = dataProtectionSettings.serviceId + "-v" + dataProtectionSettings.dataProtectionVersion + "-data-protection-accepted";

    // If this version of banner not accpeted, show it:
    if (ebiFrameworkGetCookie(dataProtectionSettings.cookieName) != "true") {
      ebiFrameworkCreateDataProtectionBanner();
    }

  } catch(err) { setTimeout(ebiFrameworkRunDataProtectionBanner, 100); }
}

/**
 * Clear the cooke. This is mostly a development tool.
 */
function resetDataProtectionBanner() {
  document.cookie = dataProtectionSettings.cookieName + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT;domain=" + document.domain + ";path=/";
  ebiFrameworkRunDataProtectionBanner('1.3');
}

/**
 * Fallback for any code that was directly calling the old cookie banner:
 * https://github.com/ebiwd/EBI-Framework/blob/6707eff40e15036f735637413deed0dcb7392818/js/ebi-global-includes/script/5_ebiFrameworkCookieBanner.js
 */
function ebiFrameworkCookieBanner() {
  console.warn('You are calling an old function name, update it to ebiFrameworkRunDataProtectionBanner();')
  ebiFrameworkRunDataProtectionBanner('1.3');
}

// execute
// ebiFrameworkRunDataProtectionBanner('1.3');
