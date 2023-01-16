/* 
 *  Description: OkHttp3 various SSL Pinning bypasses, including versions 4.2+.
 *  Authors: 	 @apps3c and @pcipolloni
 */

setTimeout(function() {

    Java.perform(function () {

		var okhttp3_CertificatePinner_class = null;
		try {
            okhttp3_CertificatePinner_class = Java.use('okhttp3.CertificatePinner');    
        } catch (err) {
            console.log('[-] OkHTTPv3 CertificatePinner class not found. Skipping.');
            okhttp3_CertificatePinner_class = null;
        }

        if(okhttp3_CertificatePinner_class != null) {

	        try{
	            okhttp3_CertificatePinner_class.check.overload('java.lang.String', 'java.util.List').implementation = function (str,list) {
	                console.log('[+] Bypassing OkHTTPv3 1: ' + str);
	                return true;
	            };
	            console.log('[+] Loaded OkHTTPv3 hook 1');
	        } catch(err) {
	        	console.log('[-] Skipping OkHTTPv3 hook 1');
	        }

	        try{
	            okhttp3_CertificatePinner_class.check.overload('java.lang.String', 'java.security.cert.Certificate').implementation = function (str,cert) {
	                console.log('[+] Bypassing OkHTTPv3 2: ' + str);
	                return true;
	            };
	            console.log('[+] Loaded OkHTTPv3 hook 2');
	        } catch(err) {
	        	console.log('[-] Skipping OkHTTPv3 hook 2');
	        }

	        try {
	            okhttp3_CertificatePinner_class.check.overload('java.lang.String', '[Ljava.security.cert.Certificate;').implementation = function (str,cert_array) {
	                console.log('[+] Bypassing OkHTTPv3 3: ' + str);
	                return true;
	            };
	            console.log('[+] Loaded OkHTTPv3 hook 3');
	        } catch(err) {
	        	console.log('[-] Skipping OkHTTPv3 hook 3');
	        }

	        try {
	            okhttp3_CertificatePinner_class['check$okhttp'].implementation = function (str,obj) {
		            console.log('[+] Bypassing OkHTTPv3 4 (4.2+): ' + str);
		        };
		        console.log('[+] Loaded OkHTTPv3 hook 4 (4.2+)');
		    } catch(err) {
	        	console.log('[-] Skipping OkHTTPv3 hook 4 (4.2+)');
	        }

		}



		const ArrayList = Java.use("java.util.ArrayList");

  		// See https://developer.android.com/reference/android/net/http/X509TrustManagerExtensions
  		const X509TrustManagerExtensions = Java.use("android.net.http.X509TrustManagerExtensions");

  			function checkServerTrusted(chain, authType, host) {
    		console.log(host);
    		const res = ArrayList.$new();
    		for (let cert of chain)
      			res.add(cert);
    		return res;
  		}

  		X509TrustManagerExtensions.checkServerTrusted.overload("[Ljava.security.cert.X509Certificate;", "java.lang.String", "java.lang.String").implementation = checkServerTrusted;
  		
  		console.log("Ready");


	});
    
}, 0);