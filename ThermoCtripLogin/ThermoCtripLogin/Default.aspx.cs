using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Text;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;


using System.Security.Cryptography;
using System.Net;
using System.IO;

namespace ThermoCtripLogin
{

    public partial class Default : System.Web.UI.Page
    {

        public string encodeString = "";
        public string encryptdata = "";
        public bool isdebug = false;
        /// <summary>
        /// CtripLoginPage
        /// </summary>
        public string encryptLoginUrl = ConfigurationManager.AppSettings["ctripUrl"];
        /// <summary>
        /// The max length when split the json data
        /// </summary>
        private readonly int maxLen = 100;
        /// <summary>
        /// The public key used to RSA encrypt
        /// </summary>
        private readonly string publicKey = @"<RSAKeyValue><Modulus>nnjiPmAX2ibGAqqM5qy2mRgm7UCwAIsTmZvbXG+3lD5oVRxMG1VFtIn/OqBmJueCSo3ONdjh+8ljYtnTS1RX6vY7NGO8307s06mXtThJSTjiiOe62Yif3ra2nLSWT1HHbWhR8rt4wb0RC5z5M9h/ZtHm8ItKdJtPJ5nOyrOU7LU=</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>";

        private string thermoID = ConfigurationManager.AppSettings["thermoID"];
        private string thermoPassword = ConfigurationManager.AppSettings["thermoPassword"];
        private string page = ConfigurationManager.AppSettings["ctripPage"];
        protected void Page_Load(object sender, EventArgs e)
        {
            if (!IsPostBack)
            {
                //the original json data
                string userdata =
                    string.Format("{{\"UserID\":\"{0}\",\"Password\":\"{1}\",\"EmployeeID\":\"{2}\",\"OrderType\":\"{3}\"}}"
                    , thermoID, thermoPassword, GetEmpStaffCode(), page);

                //userdata = "{\"UserID\":\"obk_test\",\"Password\":\"obk_test\",\"EmployeeUID\": \"wwwww\",\"OrderType\":\"Corp\",\"TO\":\"2013092201\",\"PayType\":\"T\",\"CostCenter\":\"成本中心1\",\"CostCenter2\":\"成本中心2\",\"CostCenter3\":\"成本中心3\",\"DefineFlag\":\"自定义字段\"}";

#if DEBUG
                encodeString = "http://www.corporatetravel.ctrip.com/CorpTravel/LoginCheck/LoginCheck.aspx";
#else
                //Encrypt the json data using RSAUtil and generate the encryptLoginUrl
                encodeString = encryptLoginUrl + "?" + EncryptData(userdata);
#endif
                //var result = PostToCtrip(encryptLoginUrl, EncryptData(userdata));
                //Response.Clear();
                //Response.Write(result);
            }
        }

        private string EncryptData(string data)
        {
#if DEBUG
            //send the data in clear text to ctrip server
            return data;
#else
            //Get the number of group when split the data string
            int length = data.Length;
            int index = length / maxLen;
            if (length % maxLen > 0)
                index++;
            //encrypt data by group
            String[] strs = new String[index];
            for (int i = 0; i < index; i++)
            {
                int start = maxLen * i;
                int end = Math.Min(length - start, maxLen);
                String str = data.Substring(start, end);
                //base64 encode the encrypt bytes
                String encode = Convert.ToBase64String(RSAUtils.RSAEncrypt(str, publicKey));
                strs[i] = encode;
                this.encodeString = encode;
            }
            //join the strs
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < strs.Length; i++)
            {
                encryptdata += strs[0];
                String token = "";
                if (i == 0)
                    token = "Token";
                else
                    token = "&Token" + i;
                //Urlencode the strs
                sb.Append(token);
                sb.Append("=");
                sb.Append(Server.UrlEncode(strs[i]));
            }
            return sb.ToString();
#endif
        }

        private string GetEmpStaffCode() {
#if DEBUG
            return "T100135";//for debug
#else
            //Page.User.Identity.Name
            string id = User.Identity.Name;
            if (string.IsNullOrEmpty(id)) 
            {
                return string.Empty;
            }
            using (BPMEntities bpm = new BPMEntities()) 
            {
                var emp = bpm.CM_Employees.SingleOrDefault(t => String.Compare(t.ADAccount, id, true) == 0 ? true : false);
                if (emp != null)
                {
                    //this field used to login ctrip.
                    return emp.iVantage_Code;
                }
                else {
                    return string.Empty;
                }
            }
#endif
        }

        private string PostToCtrip(string url,string postdata) {
            Uri uRI = new Uri(url);
            byte[] data = Encoding.UTF8.GetBytes(postdata);
            HttpWebRequest req = WebRequest.Create(uRI) as HttpWebRequest;
            req.Method = "POST";
            req.KeepAlive = true;
            req.ContentType = "application/x-www-form-urlencoded";
            req.ContentLength = data.Length;
            req.AllowAutoRedirect = true;

            Stream newStream = req.GetRequestStream();
            newStream.Write(data, 0, data.Length);
            newStream.Close();

            HttpWebResponse res = req.GetResponse() as HttpWebResponse;
            Stream inStream = res.GetResponseStream();
            StreamReader sr = new StreamReader(inStream, Encoding.UTF8);
            string htmlResult = sr.ReadToEnd();
            return htmlResult;
        }

    }
}
