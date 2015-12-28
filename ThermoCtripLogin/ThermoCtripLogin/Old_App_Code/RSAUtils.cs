using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;

namespace ThermoCtripLogin {
    public static class RSAUtils
    {
        public static RSAParameters RandomKey
        {
            get
            {

                RSACryptoServiceProvider.UseMachineKeyStore = true;
                RSACryptoServiceProvider rsaProvider = new RSACryptoServiceProvider(1024);
                RSAParameters p = rsaProvider.ExportParameters(true);//参数含true时表示导出带有私钥，false时不带私钥
                return p;
            }
        }

        public static string ExportKeyXML(RSAParameters key)
        {
            RSACryptoServiceProvider rsa = new RSACryptoServiceProvider();
            rsa.ImportParameters(key);
            return rsa.ToXmlString(true);
        }

        /// <summary>   
        /// RSA encrypt   
        /// </summary>   
        /// <param name="publickey"></param>   
        /// <param name="content"></param>   
        /// <returns></returns>   
        public static byte[] RSAEncrypt(string content, RSAParameters publicKey)
        {
            RSACryptoServiceProvider rsa = new RSACryptoServiceProvider();
            byte[] cipherbytes;
            rsa.ImportParameters(publicKey);
            cipherbytes = rsa.Encrypt(Encoding.GetEncoding("GBK").GetBytes(content), false);
            return cipherbytes;
        }

        /// <summary>   
        /// RSA encrypt   
        /// </summary>   
        /// <param name="publickey"></param>   
        /// <param name="content"></param>   
        /// <returns></returns>   
        public static byte[] RSAEncrypt(string content, string publicKey)
        {
            RSACryptoServiceProvider rsa = new RSACryptoServiceProvider();
            byte[] cipherbytes;
            rsa.FromXmlString(publicKey);
            cipherbytes = rsa.Encrypt(Encoding.GetEncoding("GBK").GetBytes(content), false);
            return cipherbytes;
        }

        /// <summary>   
        /// RSA decrypt   
        /// </summary>   
        /// <param name="privatekey"></param>   
        /// <param name="content"></param>   
        /// <returns></returns>   
        public static string RSADecrypt(string content, RSAParameters privateKey)
        {
            RSACryptoServiceProvider rsa = new RSACryptoServiceProvider();
            byte[] cipherbytes;
            rsa.ImportParameters(privateKey);
            byte[] bytes = Convert.FromBase64String(content);
            cipherbytes = rsa.Decrypt(bytes, false);

            return Encoding.GetEncoding("GBK").GetString(cipherbytes);
        }

        /// <summary>   
        /// RSA decrypt   
        /// </summary>   
        /// <param name="privatekey"></param>   
        /// <param name="content"></param>   
        /// <returns></returns>   
        public static string RSADecrypt(string content, string privateKey)
        {
            RSACryptoServiceProvider rsa = new RSACryptoServiceProvider();
            byte[] cipherbytes;
            rsa.FromXmlString(privateKey);
            byte[] bytes = Convert.FromBase64String(content);
            cipherbytes = rsa.Decrypt(bytes, false);

            return Encoding.GetEncoding("GBK").GetString(cipherbytes);
        }
    }
}
