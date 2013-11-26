import unittest
from itertools import zip_longest
from lexer import Tag, lex_file


class LexerTests(unittest.TestCase):
    def assert_lists_are_same(self, xs, ys):
        for (i, (x, y)) in enumerate(zip_longest(xs, ys)):
            self.assertEqual(x, y, msg='Elements at index #{0} do not match: {1!r} != {2!r}'.format(i, x, y))

    def test_presol_valid1(self):
        expected = [
            Tag('<PRESOL>'), '\n',
            Tag('<DATE>'), '0101\n',
            Tag('<YEAR>'), '07\n',
            Tag('<AGENCY>'), 'Department of the Air Force\n',
            Tag('<OFFICE>'), 'US Central Command Air Force/A4-LGCP\n',
            Tag('<LOCATION>'), '376 AEW/ECONS, Kyrgyzstan\n',
            Tag('<ZIP>'), '09353\n',
            Tag('<CLASSCOD>'), '61\n',
            Tag('<NAICS>'), '335311\n',
            Tag('<OFFADD>'), 'Department of the Air Force, US Central Command Air Force/A4-LGCP, 376 AEW/ECONS, Kyrgyzstan, 376 AEW/ECONS, APO, AE, 09353, UNITED STATES\n',
            Tag('<SUBJECT>'), '61 -- 750 KVA TRANSFORMER\n',
            Tag('<SOLNBR>'), 'F38604-07-Q-C006\n',
            Tag('<RESPDATE>'), '010607\n',
            Tag('<ARCHDATE>'), '01212007\n',
            Tag('<CONTACT>'), 'Veronica Bravo, Contracting Officer, Phone 011996502555117, Email veronica.bravo@maab.centaf.af.mil - Veronica Bravo, Contracting Officer, Phone 011996502555117, Email veronica.bravo@maab.centaf.af.mil\n',
            Tag('<DESC>'), 'TRANSFORMER, 750 KVA FOR MANAS AIR BASE, KYRGYZSTAN\n',
            Tag('<LINK>'), '\n',
            Tag('<URL>'), 'http://www.fbo.gov/spg/USAF/USCENTAF/376AEWECONS/F38604-07-Q-C006/listing.html\n',
            Tag('<DESC>'), 'Link to FedBizOpps document.\n',
            Tag('<POPCOUNTRY>'), 'KYRGYZSTAN\n',
            Tag('<POPZIP>'), '09353\n',
            Tag('<POPADDRESS>'), '376 AEW/ECONS\nAPO AE\n',
            Tag('</PRESOL>'), '\n\n'
        ]
        observed = list(lex_file('testfiles/presol_valid1'))
        self.assert_lists_are_same(observed, expected)

    def test_amdcss(self):
        expected = [
            Tag('<AMDCSS>'), '\n',
            Tag('<DATE>'), '0711\n',
            Tag('<YEAR>'), '07\n',
            Tag('<AGENCY>'), 'Department of the Army\n',
            Tag('<OFFICE>'), 'ACA, Pacific\n',
            Tag('<LOCATION>'), 'ACA, Fort Richardson\n',
            Tag('<ZIP>'), '99505-0525\n',
            Tag('<CLASSCOD>'), '12\n',
            Tag('<NAICS>'), '333314\n',
            Tag('<OFFADD>'), 'ACA, Fort Richardson, Regional Contracting Office, Alaska, ATTN:  SFCA-PRA-A, PO Box 5-525, BLDG 600 2nd FL, Fort Richardson, AK  99505-0525\n',
            Tag('<SUBJECT>'), '12--50 Each TA33-8 3x30 ACOG Scope features a Dual Illumination Amber Chevron .223 Ballistic Reticle and comes with a TA60 Compact ACOG  M16 base Flattop Adapter Mount.\n',
            Tag('<SOLNBR>'), 'WC1SH37142G031\n',
            Tag('<RESPDATE>'), '071607\n',
            Tag('<ARCHDATE>'), '09142007\n',
            Tag('<CONTACT>'), 'Jeffrey Roberts, 907 384-7104\n        ',
            Tag('<DESC>'), '(i) This is a combined synopsis/solicitation for commercial items prepared in accordance with the format in Subpart 12.6, as supplemented with additional information included in this notice. This announcement constitutes the only solicitation; propos als are being requested and a written solicitation will not be issued. (ii) This Combined Synopsis/Solicitation is issued as a request for quotation (RFQ) WC1SH37142G031.   (iii)The solicitation document and incorporated provisions and clauses are those in effect through Federal Acquisition Circular 2005-17 (iv)This acquisition is reserved for small business concerns. The associated NAICS code for this acquisition is 333314 and small business size standard is 500 employees. (v)Line Item 0001 The TA33-8 3x30 ACOG Scope features a Dual Illumination Amber  Chevron .223 Ballistic Reticle and comes with a TA60 Compact ACOG  M16 base Flattop Adapter Mount. (vi) Weapon scope  50 each  (vii) FOB destination: delivery to Fort Richardson, Alaska by Aug 15, 2007. (viii)The following provisions apply to this acquisition,  FAR 52.212-1 Instructions to Offerors--Commercial (JAN 2006)  (ix)FAR 52.212-2 Evaluation -- Commercial Items (Jan 1999) The Government will award a contract resulting from this solicitation to the responsible offeror whose offer conforming to the solicitation will be most advantageous to the Government, price and ot her factors considered. The following factors shall be used to evaluate offers: Price will be a more significant evaluation factor than technical, availability and past performance combined. However technical capability of the item offered to meet the Gove rnment requirement, availability, and past performance will be weighed in conjunction with price (x) All offers must include a completed copy of the provision at FAR 52.212-3 offeror representations and certifications--commercial Items (JUN 2006) or be completed on the ORCA website.  (xi) FAR 52.212-4 Contract Terms and Conditions -- Commercial Items (SEP 2005), (xii) FAR 52.212-5 Contract Terms and Conditions Required to Implement Status or Executive OrdersCommercial Items (SEP 2006),  (xiii) FAR 52.214-21 -- Descriptive Literature FAR 52.219-6 Notice of Total Small Business Set-Aside (JUNE 2003), FAR 52.222-3, Convict Labor (JUNE 2003), FAR 52.222-19 Child Labor-Cooperation with Authorities and Remedies (JAN 2006), FAR 52.222-21 Prohibi tion of Segregated Facilities (Feb 1999), 52.222-22 Previous Contracts and Compliance Reports (FEB 1999), FAR 52.222-26 Equal Opportunity (APR 2002), FAR 52.225-13, Restrictions on Certain Foreign Purchases (FEB 2006), FAR 52.232-33 Payment by Electronic F unds TransferCentral Contractor Registration (OCT 2003), FAR 52.247-34 F.O.B. Destination (NOV 1991), DFAR 252.204-7003 Control Of Government Personnel Work Product (APR 1992), DFAR 252.232-7003 Electronic Submission of Payment Requests (MAY 2006), DFAR 2 52.232-7010 Levies on Contract Payments (DEC 2006), DFAR 252.243-7001 Pricing of Contract Modifications (DEC 1991),   (Xiv)The full text of clauses and provisions can be accessed at the following web addresses: www.acqnet.gov/FAR and www.acq.osd.mil/dpap/dars/dFARs/index.htm  (xv) No applicable number notes (xvi) All offers are due no later than 11:00 AM, Alaska Time, 16 July 2007 via fax (907) 384-7112 or email jeffrey.c.roberts1@us.army.mil   (xvii)For further information contact Jeff Roberts @ (907) 384-7104.\n',
            Tag('<LINK>'), '\n',
            Tag('<URL>'), 'http://www.fbo.gov/spg/USA/DABQ/DABQ03/WC1SH37142G031/listing.html\n',
            Tag('<DESC>'), 'Link to FedBizOpps document.\n',
            Tag('<EMAIL>'), '\n',
            Tag('<ADDRESS>'), 'jeffrey.c.roberts1@us.army.mil\n',
            Tag('<DESC>'), 'ACA, Fort Richardson\n',
            Tag('<SETASIDE>'), 'Total Small Business\n',
            Tag('<POPADDRESS>'), 'ACA, Fort Richardson Regional Contracting Office, Alaska, ATTN:  SFCA-PRA-A, PO Box 5-525, BLDG 600 2nd FL Fort Richardson AK\n',
            Tag('<POPZIP>'), '99505-0525\n',
            Tag('<POPCOUNTRY>'), 'US\n',
            Tag('</AMDCSS>'), '\n'
        ]
        observed = list(lex_file('testfiles/amdcss_valid1'))
        self.assert_lists_are_same(observed, expected)

if __name__ == "__main__":
    unittest.main()
