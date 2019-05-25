# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com       
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################



from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError 
from openerp import models, fields, api, _
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
 
 
class fleet_gps_process(models.TransientModel):
    _name = 'fleet.gps.process'
    _description = "Fleet Processing GPS point"
 
    date_preluc = fields.Datetime(string="DataPreluc")
    date_end_preluc = fields.Datetime(string="DataEndPreluc")



    @api.multi
    def process_all(self):
        vehicle_ids = self.env['fleet.vehicle'].search([('on_line','=',True)])
        for vehicle in vehicle_ids:
            self.process_vehicle(vehicle)



    @api.multi
    def process_vehicle(self, vehicle, DataPreluc=None, DataEndPreluc=None):
      DataPreluc = self.GetDataPreluc(vehicle,DataPreluc)  



    @api.nodel
    def GetDataPreluc(self,vehicle,DataPreluc):
        DataPreluc_M = DataPreluc
        # se pleaca de la premisa ca masina merge cu motorul pornit!
        if not DataPreluc:
           DataPreluc_M =  vehicle.processing_date  or '2000-01-01 00:00:00'
           DataPreluc = DataPreluc_M
           
        """
        poate masina mergea cand am facut ultima prelucrare asa ca o reiau
         |-----------|--------|-----------|
                        ^ data specificata
         ^  data de la care se reface procesarea  
          se refac doua trasee.   
        """          
        fleet_gps_route = self.env['fleet.gps.route'].search([('vehicle_id','=',vehicle.id),
                                                              ('date_end','<',DataPreluc)],
                                                              limit=1, order='date_begin DESC')
        if fleet_gps_route:
            DataPreluc = fleet_gps_route.date_begin
        else:
            # nu a fost prelucrata aceasta masina!
            fleet_gps_point = self.env['fleet.gps.point'].search([('vehicle_id','=',vehicle.id)],
                                                              limit=1, order='date')
            if fleet_gps_point:
                DataPreluc = leet_gps_point.date
                vehicle.write({'processing_date':fleet_gps_point.date,'on_line':False})
        
        # zile = abs(strtotime($DataPreluc)-strtotime($DataPreluc_M))/86400;
        if zile > 1:
            # "Prea multe zile ($zile) intre data determinata ( $DataPreluc ) si cea solicitata ($DataPreluc_M) "); 
            DataPreluc = DataPreluc_M
             
        return DataPreluc

"""
    function GetDataPreluc($idm,$DataPreluc='NA'){

        $this->db->trans_begin();
        
        $this->Mesaj(  "Data $DataPreluc  GMT specificata initial ");
        $DataPreluc_M = $DataPreluc;
        // se pleaca de la premisa ca masina merge cu motorul pornit!
         if ($DataPreluc == 'NA') {
            $DataPreluc_M = $this->GetData->GetDataPreluc($idm);
            $DataPreluc = $DataPreluc_M;
            $this->Mesaj(  "Data $DataPreluc  GMT citita din t09masini");
        }
        $DataPreluc_M = date('Y-m-d H:i:s',strtotime($DataPreluc_M ));
        $DataPreluc =  date('Y-m-d H:i:s',strtotime($DataPreluc ));
        // poate masina mergea cand am facut ultima prelucrare asa ca o reiau
        /// |-----------|--------|-----------|
        ///                ^ data specificata
        /// ^  data de la care se reface procesarea  
        ///  se refac doua trasee.
          
           
        $query = $this->db->query(" SELECT max(DL) as DL FROM t09pgpsX WHERE M = '$idm' AND PL < '$DataPreluc' ");
        $row = $query->row();
        if ($row->DL!='')  {
            $DataPreluc = date('Y-m-d H:i:s',strtotime( $row->DL) );
            $this->Mesaj("Data de procesare rederminata");
        }
        else {
            // nu a fost prelucrata aceasta masina!
            $this->Mesaj('Prima procesare');
            $query = $this->db->query(" SELECT min(DP) as DP FROM t00pgps_a WHERE MS = '$idm'  ");
            $row = $query->row();
            if ($row->DP!='') $DataPreluc = date('Y-m-d H:i:s',strtotime($row->DP ));
            $sql  = "UPDATE t09masini SET  DataPreluc = '$DataPreluc', Online = 'Nu' WHERE MS = '$idm'" ;
            $this->db->query($sql,false);
        }
        $zile = abs(strtotime($DataPreluc)-strtotime($DataPreluc_M))/86400;
        if ( $zile > 1)
            {
                $this->Mesaj(  "Prea multe zile ($zile) intre data determinata ( $DataPreluc ) si cea solicitata ($DataPreluc_M) "); 
                $DataPreluc = $DataPreluc_M;
            }
         
        // acum se verifica in tabela de trasee daca exista data PL  se selecteaza linia DL care pentru linia
        //$DataPreluc = gmdate('Y-m-d H:i:s', strtotime($DataPreluc));  // reconvertita in GMT  ca trebuie sa selectez din t00pgps_a

        $this->Mesaj(  "Data de la catre trebuie facuta procesarea <b>".$DataPreluc ." GMT </b> ");
        return $DataPreluc;


        if ($this->db->trans_status() === FALSE){
            $this->db->trans_rollback();
        }
        else{
            $this->db->trans_commit();
        } 
        
    }
"""


	"""

Class MProcesare extends CI_Model {


    function ProcesareMasina($idm,$DataPreluc='NA',$DataEndPreluc='NA'){
         $this->Mesaj("   -------------START-----------------------------  ");
        
        $DataPreluc = $this->GetDataPreluc($idm,$DataPreluc);  

        $this->Mesaj( "ProcesareMasina($idm) si $DataPreluc GMT si $DataEndPreluc GMT ");
        
        if ($DataPreluc!='NA' and $DataEndPreluc!='NA'){
            $sql  = "SELECT count(*) as NrTrasee FROM t09pgpsX WHERE M = '$idm' AND PL > '$DataPreluc' AND DL < '$DataEndPreluc' " ;
            $query = $this->db->query($sql);
            $row = $query->row();
            $this->Mesaj("In perioada exista: ".$row->NrTrasee);
        }



        
        $trasee = false;
        $trasee = $this->ProcesarePoz($idm,$DataPreluc,$DataEndPreluc,50000);


        if (($trasee===false) || (sizeof($trasee)==0)  ){
            $this->Mesaj( "Nu sunt pozitii de procesat ");
            return false;
        }

        $DataPreluc = $this->Salveaza_Trasee($idm,$trasee );

        if ($DataEndPreluc=='NA') 
            $this->UpdateDataPreluc($idm,$DataPreluc);
        $this->Mesaj("   -------------STOP-------------------  ");    
        return $DataPreluc;
        
    }
    
    function Salveaza_Trasee($idm,$trasee ){
        
        $this->db->trans_begin();
        
        $this->Mesaj( "<b> Au fost generate ".sizeof($trasee)." linii de trasee. </b> ");
        
        $tra_first = $trasee[0];
        $tra_last = $trasee[sizeof($trasee)-1];
        
        $DL = $tra_first['DL'];
        $PL = $tra_last['PL'];
        
        $this->Mesaj( "<b> trasee in intervalul ---(--$DL--$PL--)- GMT-- </b> ");
        
        $sql  = "DELETE FROM t09pgpsX WHERE M = '$idm' AND PL > $DL and DL < $PL " ;
        $this->db->query($sql,false);
        
        
        // m/s = 3,6
        
        $sql = "INSERT INTO t09pgpsX (M, DL,  PL,  Lti,  Lni,  Ltf,  Lnf, Trul, Tmot, Trac, Vmx,  Ef, Dist_rap,  Tst,  NrS, Tsts, TFsemn, DistFsemn, POIp, POIs,  iduri, Cale, FD ) VALUES ";
        $values = '';
 
        //dump($trasee);
        
        foreach ($trasee as $tra){
            $values .= "\n,( '$idm' ,".implode(" , ", $tra).")";
        }
        $sql .= substr( $values,2);
        $this->db->query($sql,false);
            
            
        //$DataPreluc = gmdate('Y-m-d H:i:s',  strtotime(str_replace("'","",$tra['PL'])) );  /// salvez data in format GMT !!!!
        $tra = $trasee[sizeof($trasee)-1];
        $DataPreluc = str_replace("'","", $tra['PL']);
        $this->Mesaj( "Date procesate pana la:<b>". $tra['PL']." GMT  </b> ");
        // TODO: De scris in PHP.
        $sql = " UPDATE t09pgpsX SET FD = ".
                 " IF (     DATE(DL) =  DATE(PL),     fgGetLocalTime (DATE(DL)), ".
                 "   IF (     TIMEDIFF(DATE_FORMAT( fgGetLocalTime (DL),     '%Y-%m-%d 23:59:59' ),     fgGetLocalTime (DL)) > ".
                         "   TIMEDIFF(fgGetLocalTime (PL),     DATE_FORMAT( fgGetLocalTime (DL),     '%Y-%m-%d 23:59:59'    )),    date(DL),    date(PL) ) ) ".
                 " WHERE M = '$idm' and FD IS NULL;";
        $this->db->query($sql,false);
        
        if ($this->db->trans_status() === FALSE){
            $this->db->trans_rollback();
        }
        else{
            $this->db->trans_commit();
        }         
        
        return $DataPreluc;
    }
    



    function UpdateDataPreluc($idm,$DataPreluc){
            $sql  = "UPDATE t09masini SET  DataPreluc = '$DataPreluc', Online = 'Nu'  WHERE MS = '$idm'" ;
            $this->db->query($sql,false);            
        }

//// ---------------------------------------------------------------------------------------------------------------------------------

                // functia de initializare foaie de parcurs
        private function Init_tra($row){
            $tra['DL'] =  date('"Y-m-d H:i:s"',   $row['DP'] ) ;
            $tra['PL'] =  date('"Y-m-d H:i:s"',   $row['DP']) ;
            $tra['Lti'] = $row['Lat'];
            $tra['Lni'] = $row['Lng'];
            $tra['Ltf'] = $row['Lat'];
            $tra['Lnf'] = $row['Lng'];
            $tra['Trul'] = 0;    // timpul de rulare
            $tra['Tmot'] = 0;    // timpul de functionare motor
            $tra['Trac'] = 0;    // timp de functionare termoking
            $tra['Vmx'] = 0;     // viteza maxima
            $tra['Ef'] =  0;     // distanta efectiva
            $tra['Dist_rap'] =  0;     // distanta parcursa rapid
            $tra['Tst'] = 0;     // 
            $tra['NrS'] = 0;     // numarul de stationari
            $tra['Tsts'] = 0;    // timpul stationarilor scurte
            $tra['TFsemn'] = 0;
            $tra['DistFsemn'] = 0;
            $tra['POIp'] = 0;
            $tra['POIs'] = 0;
    //        $tra['Points']= "''";
            $tra['iduri']= "''";
            $tra['Cale']="''";
            $tra['FD']="null";
            //dump($tra);
            return $tra;
        }


    function ProcesarePoz($idm,$DataPreluc,$DataEndPreluc,$max_pozitii=50000){


        
        $this->Mesaj(  "ProcesarePoz($idm,$DataPreluc,$DataEndPreluc,$max_pozitii)");

        $begin_time = microtime_float();

        //echo ($idm);
        //echo " Procesare de la data " . $DataPreluc ."  <br>";


        /// ------- selectie parametri --->
        $query = $this->db->query("SELECT Ben, TipMont+0 as TipMont, Vmx FROM t09masini WHERE MS = '$idm'");  
        if ($query->num_rows()==0) return false;
        $row = $query->row();
        $idben = $row->Ben;
        $Vmx = $row->Vmx;
        if (($row->TipMont & 8 ) == 8) $Semnal_M = True;
        else $Semnal_M = False; 

    
            
        $query = $this->db->query("SELECT  * FROM t09firme WHERE Ben = $idben");
        if ($query->num_rows()==0) return false;
        $par  =  $query->result_array() ;
        $par  =  $par[0];
        $par['Semnal_M']  =  $Semnal_M;
        $par['Vmx']  =  $Vmx;
        
    
        /// <------ selectie parametri ----


        // selectez prin grupare pentru a elimina pozitiile care sunt dublate
        // nu pot pentru ca vreau sa selectez si IDul
        // selectie date in memorie --
        if ($DataEndPreluc == 'NA') {
            $sql = "SELECT  id, DP, Lat, Lng, Vit, Intrare+0 as Intrare , Alarm ".
                     " FROM t00pgps_a ".
                     " WHERE  MS = '$idm' and DP >= '$DataPreluc'    order by t00pgps_a.DP  limit $max_pozitii";
        }
        else {
                $max_pozitii = $max_pozitii * 2 ;
                $sql = "SELECT  id, DP, Lat, Lng, Vit, Intrare+0 as Intrare , Alarm ".
                     " FROM t00pgps_a ".
                     " WHERE  MS = '$idm' and DP >= '$DataPreluc'   and DP <= '$DataEndPreluc' order by t00pgps_a.DP  limit $max_pozitii";        
        }
        //$this->Mesaj($sql);
        $query_poz = $this->db->query($sql);
        $this->Mesaj(  'Nr de intregistrari de procesat:'. $query_poz->num_rows()) ;
        if ($query_poz->num_rows()==0) return false;

        $end_time = microtime_float();
        $dif_time = round($end_time - $begin_time, 4);
        $this->Mesaj( "Preluarea datelor din baza de date a durat $dif_time secunde");
        
        
        $pozitii = $query_poz->result_array();

         

        /// ------------  preprocesare ----------->
        // prin preprocesare se calculeaza distantele intre puncte si viteza calc
        //$pozitii[0]['DP'] =     strtotime($DataPreluc . " GMT") ;        // nu trebuie de la data ultimei procesari ???
        //$pozitii[0]['DP'] =     strtotime($pozitii[0]['DP'] . " GMT") ;  // trebuie data de inceput de interval

        $row_ant = $pozitii[0];
        $row_ant['DP'] =     strtotime($row_ant['DP'] . " GMT")   ;
        //dump($row_ant);
        // todo: sunt prea multe caclule pentru viteza
        // se incepe procesare a de la pozitia 1, pozitia zero e salvat in row_ant
        $key = 0;
        $pozitii_p = array();
        while ($key <  sizeof($pozitii)-1) {
             
            $row = $pozitii[$key];
            if ($row['Alarm'] == '95') {                
                $key++;
                continue;    
            }
            if ($row['Lat'] == 0 ) {                
                $key++;
                continue;    
            }
            if ($row['Lng'] == 0 ) {                
                $key++;
                continue;    
            }
            $row['DP'] =     strtotime($row['DP'] . " GMT")   ;
            if ($row['DP'] == $row_ant['DP']){    
                $key++;
                continue;    
            }            
                
            $row['Motor'] = (($row['Intrare'] & 8 ) == 8 );
            $row['Racire'] = (($row['Intrare'] & 16 ) == 16 );

            $delta_dist = distance($row['Lat'],$row['Lng'],$row_ant['Lat'],$row_ant['Lng']);
            $row['Dist']= round($delta_dist,6);                               // km
            if ($row['Dist'] > $par['dist_fara_semn'])     $row['semanl'] = false;
            else  $row['semanl'] = true;


                        
            $row['DP_loc'] =  date('"Y-m-d H:i:s"',   $row['DP']   ) ;

            $row['dT'] = ($row['DP'] - $row_ant['DP']) / 60;                  //minute

            if ($row['dT'] >0) $row['VitCalc'] =  $row['Dist']/$row['dT']*60;
            else $row['VitCalc'] = 0;
                
            /*
             if (($row['VitCalc']>= $row['Vit']*2) && ($row['dT'] < 0.017)){
            //daca viteza calculata este prea mare si dT este de o sec
            $row['VitCalc'] = $row['Vit'];
            } */

            // identifc daca nu a dat la chei si a oprit !
            /*             if ($key>1) {
                if(  ( $pozitii[$key-1]['Motor'] == 0) && ( $row['Motor'] == 1) && ( $pozitii[$key+1]['Motor'] == 0) ) {
            $row['Motor'] = 0;
            //     echo "Pornire falsa ! $key";
            }
            } */

            // nu cred ca o masina o sa mearga cu 200 de km la ora !!
            if  ($row['VitCalc']>= 200 && $row['dT'] > 1 ) {
                //dump("Ce viteza!");
                //dump($row);
                $this->Mesaj("Viteza calculata ".$row['VitCalc']." la id ".$row['id']);
                $row = $row_ant;
                $row['dT'] = 0;
                $row['Dist'] = 0;
                $row['semanl'] = false;
            }

            

            /*
             if ($row['DP'] == $row_ant['DP']){
            $this->Mesaj( "E doar o schimbare de status!");
            $this->Mesaj( "Anterior!");
            dump($row_ant);
            $this->Mesaj( "Curent!");
            dump($row);
            }
            */
            $pozitii_p[]= $row;
            $row_ant = $row;
            $key++;
        }  //terminat de preprocesat
        /// <-----------  preprocesare -----------
        $this->Mesaj('Preprocesat finalizata. pozitii='.sizeof($pozitii_p));
        // am obtinut o lista de pozitii cu campuri caclulate suplimentare
        $pozitii = $pozitii_p;
        unset($pozitii_p);
        // dump($pozitii );
        
        $trasee = array();    // tabelul in care se insereaza traseele  prelucrate
        
        if (sizeof($pozitii)<=1) return $trasee;
        
        $distanta = 0;
        $distanta_rap = 0;

        $start = 0;
        $VitMax = 0 ;

        $posibil_stop = false;
        $posibil_start = false;
        $save  = false;



        $key = 1;
        $key_end = 0;
        $key_start = 0;
        $key_fin = 0 ;
        $mergea =  true;
        $row_ant = $pozitii[0];
        $row_start = $pozitii[0];   // de unde incepe masina sa mearga
        $row_end = $pozitii[0];     // unde masiana s-a oprit
        $row_fin = $pozitii[0];     // final de traseul pozitia de la care masina incepe de mearga din nou
        $pct = 0;
        $puncte = array(array(0,0));
        $iduri = array(); // in care salvez pozitiile
        $timp_racire = 0;
        $timp_motor = 0;  // timpul de rulare (cu motorul pornit )
        $timp_fara_semanl = 0;
        $dist_fara_semanl = 0;

        $timp_opriri_scurte = 0;
        $nr_opriri = 0;  // nr de opriri scurte

        // este foarte importanta ordinea in care sunt declarate pentru ca in fucntie de asta se face insert
        //DL,  PL,  Lti,  Lni,  Ltf,  Lnf, Trul,Tmot, Trac,  Vmx,  Ef,  Tst,  NrS, TFsemn, DistFsemn, POIp, POIs, Points
        
        
        $tra = $this->Init_tra( $row_ant);


        // am sa fac un buffer cu un nr de pozitii
        // si am sa determin cate puncte se afla in interilorul unui cerc cu raza unui jiter

        // trebuie sa trec la alta linie daca distanta dintre doua puncte este mai mare de ?? si interpretez ca lipsa semnal

        // se pleaca de la o pozitie in care masina a pornit


        //$this->Mesaj( "Pozitia de la care se pleaca !");
        //dump($row_start);

        //    -------------- start-------------end-----------------fin=start-----------end-----------------fin
        /// -- stationare            rulare         stationare                 rulare         stationare
        
        $nr_pozitii = sizeof($pozitii); 
        while ($key <  $nr_pozitii-1) {
             
            $row = $pozitii[$key];
            $row_ant =  $pozitii[$key-1];

            $delta_dist = $row['Dist'];
        
                
            if ($row['Racire'] ) $timp_racire += $row['dT'];
            if ($row['Motor'] && $par['Semnal_M'] )  $timp_motor += $row['dT'];   /// se inregistreaza functionare motor daca bitul este functional
             
                        
            if ($VitMax < $row['Vit'])  $VitMax = $row['Vit'] ;
    
            /// calculez conditiile de stop si start
            if ($par['Semnal_M']) {
                $cond_stop =    ($row['Motor'] == 0) || ($row['Vit'] == 0) || ( ($delta_dist < $par['dist_max_jiter']) && ($row['Vit']<$par['vit_min']));
                $cond_start =   ($row['Motor'] != 0) ||                         ($delta_dist > $par['dist_max_jiter']) || ($row['Vit'] > $par['vit_max_jiter'] );
            }
                
            else {
                $cond_stop =  ($row['Vit'] == 0) || ( ($delta_dist < $par['dist_max_jiter']) && ($row['Vit'] < $par['vit_min']));
                $cond_start =                         ($delta_dist > $par['dist_max_jiter']) || ($row['Vit'] > $par['vit_max_jiter'] );    
            }
                

                
            if ($mergea) {    // trebuie sa testez ca masina merge in continuare
                if ($row['Lng']<>$row_ant['Lng'] ||  $row['Lat']<>$row_ant['Lat'] ) {
                    $puncte[$pct][0] =   $row['Lng'];
                    $puncte[$pct][1] =   $row['Lat'];
                    $iduri[$pct] = $row['id'];
                    $pct++;                    
                }


                $distanta +=  $delta_dist;   // se calculeaza distanta numai cand masina se deplaseaza
                if ($row['Vit']>=$par['Vmx'])
                    $distanta_rap +=  $delta_dist; 

                if (!$par['Semnal_M'] && $row['Vit']>$par['vit_min']) // bitul motor nu functioneaza asa ca calculez ca timpul de functionare  motor e timpul de  in care masina are o oarecare viteza            
                         $timp_motor += $row['dT'];
                        
                if (!$row['semanl']){
                    $timp_fara_semanl += $row['dT'];
                    $dist_fara_semanl += $delta_dist;
                }

                
                // ca sa mearga trebuie sa am cateva puncte!!!
                if ($pct > 3 ) {
                    //simplific linia daca sunt pozitii consecutive -- probabil alte alarme
                    if($puncte[$pct-2][0] == $row['Lat'] && $puncte[$pct-2][1] == $row['Lng'] ) $pct--;

                    if  (!$posibil_stop) {//masina mergea si testez sa vad daca s-a oprit
                        if ($cond_stop)    {
                            // a fost oprint motorul, logic ar fi ca masina sa nu mai mearga
                            // distanta fata de punctul anterior e zero - e posibi sa fie semnal de schimbare directie
                            // Viteza este Zero -- si ce fac la stop ??
                            // distanta totoala de mai mica decat dublul distentei minime                        
                            $row_end = $row;
                            $key_end = $key;
                            $posibil_stop = true;
                            $nr_opriri++;
                        }
                    }
                    else { // daca anterior s-a detectat o posibilitate de oprire (am dubii ca masina merge)
                        // se pastreaza conditia de stop ??
                        $timp_stop = ( $row['DP']  - $row_end['DP']  ) / 60;
                        if (!$cond_stop || $cond_start){
                            $posibil_stop = false;
                            $timp_opriri_scurte += $timp_stop;  // contorizerz timpul total al opririlor scurte
                            //    echo "<br> Pornire dupa o stationare de  $stop <br>";                            
                        }
                        else {                          
                            if ( $timp_stop >= $par['timp_oprire'] ) {
                                //$this->Mesaj("timp_stop = $timp_stop");
                                // chiar s-a oprit un timp mai mare si se considera stationare
                                // inainde de salvare se verifica ca s-a parcus distanta minima !
                                //if ($distanta > $par['dist_min'])     $save = true;
                                //else  { $mergea = false;  }   // nu mai salva si treci in celalat regim!
                                $save = true;  /// conditia de salvare a fost inchiata se poate genera acum un traseu -- mai contorisez timpul de la capatul traseului
                                //$row_end = $pozitii[$key_end];  // daca motorul e pornit se considera stationarea de ??? oprirea motorului
                                $nr_opriri--;   // nu e o oprire scurta
                            }
                        }
                    }
                }  /// sunt mai mult de 3 puncte
            }  // <-- masina merge
            else {   // stationare acum trebuie sa verific daca nu cumva masina a plecat
                // aici se verifica daca masina stationeaza in continuare
                

                            
/*                
                if  ( $cond_start ) {
                    ///  aici era si ($row['Motor'] == 1)  dar nu trebuie
                    /// daca masina stationeaza si soferul da o chei la masina nu insemana ca si porneste din nou la drum

                    if  (!$posibil_start) {
                        $row_fin = $row;
                        $key_fin = $key;
                    }
                    //echo "Salvare foratata $key_start <br>";
                    $save = true;
                }
*/
                if  (!$posibil_start) {
                    if ( $cond_start )    {    // a fost oprint motorul, logic ar fi ca masina sa nu mai mearga
                        $row_fin = $row;
                        $key_fin = $key;
                        $posibil_start = true;
                    };
                }
                else {                     // daca anterior s-a detectat o miscare
                    $dist_fin = distance($row['Lat'],$row['Lng'],$row_end['Lat'],$row_end['Lng']);  // distanta de la punctul in care a stationat
                    if  (  $dist_fin >= $par['dist_min']  ) { // chiar masina a pornit
                            //$this->Mesaj("delta_dist: $delta_dist");
                            //$this->Mesaj("dist_fin: $dist_fin");
                            //$this->Mesaj("dist_min: ".$par['dist_min']);
                            $save = true;   // trebuie sa salvez traseul curent si sa incep altul ca masina se deplaseaza!!!    
                        }                     
                    else 
                    if (!$cond_start || $cond_stop) 
                        $posibil_start = false;
                    }

            }  // <- stationare

            if (($key ==  $nr_pozitii-4) && $mergea){
                $save = true; // fortare 
                $row_end = $row;
                $key_end = $key;
                $this->Mesaj( "Fortez oprirea traseului din deplasare la key = $key");
            }
            if (($key ==  $nr_pozitii-3) && !$mergea){
                $save = true; // fortare 
                $row_fin = $row;
                $key_fin = $key;
                $this->Mesaj( "Fortez oprirea traseului din stationare la key = $key");
            }

            if ($save) {
                if ($mergea ) {
                    // am primit comanda de salvare a intormatiilor de la capatul unei deplasari
                    // salvez datele si astept ca sa se masina sa plece din nou pentru a trece la un alt traseu

                    // este foarte importanta ordinea in care sunt declarate
                    //DL,  PL,  Lti,  Lni,  Ltf,  Lnf, Trul,  Vmx,  Ef,  Tst,  NrS, POIp, POIs, Points
                    $tra['DL'] =  gmdate("'Y-m-d H:i:s'",   $row_start['DP']    ) ;       // in format GMT
                    $tra['PL'] =  gmdate("'Y-m-d H:i:s'",   $row_end['DP']   ) ;
                    if (gmdate("'Y-m-d'",   $row_start['DP']) == gmdate("'Y-m-d'",   $row_end['DP'])) {
                        $tra['FD'] = gmdate("'Y-m-d'",   $row_start['DP']);
                    }
                    
                    $tra['Lti'] = $row_start['Lat'];
                    $tra['Lni'] = $row_start['Lng'];
                    $tra['Ltf'] = $row_end['Lat'];
                    $tra['Lnf'] = $row_end['Lng'];
                    $timp_total = ( $row_end['DP']  - $row_start['DP']  ) / 60;     // timpul total de rulare in MIN
                    $trul = $timp_total - $timp_opriri_scurte;
                    $tra['Trul'] = $timp_total;                       //Timpul de rulaj efectiv pe o portiune (exclusiv opririle scurte)
                    $tra['Tmot'] = 0;
                    $tra['Trac'] = 0;                              //Timp de functionare termoking
                    $tra['Vmx'] = round($VitMax,1);             // viteza maxima
                        
                    // din cauza lipsei de semnal e posibl ca viteza sa nu fie cea buna
                    $Vit_calc = 0;
                    if ($timp_total > 0) {
                        // cu e posibil ca timpul total sa nu fie mai mare de zero ?
                        $Vit_calc = $distanta/$timp_total*60;
                    }
                    if ($Vit_calc>$VitMax) $tra['Vmx'] = round($Vit_calc,1);
                        
                    $tra['Ef'] =  round( $distanta*$par['CAR'], 3);   // distanta efectiva
                    $tra['Dist_rap'] =  round( $distanta_rap*$par['CAR'], 3);   // distanta efectiva cu viteza rapida
                    $tra['Tst'] = 0;                            // 'Timp de stationare la capatul portiunii ',
                    $tra['NrS'] = $nr_opriri;
                    $tra['Tsts'] = $timp_opriri_scurte;
                    $tra['TFsemn'] = $timp_fara_semanl;
                    $tra['DistFsemn'] = $dist_fara_semanl;
                    $tra['POIp'] = 0;
                    $tra['POIs'] = 0;


//                    $tra['Points'] = "'(".json_encode($puncte,JSON_NUMERIC_CHECK).")'";
                    // se nu pun si gilemele in string
                    //$tra['Points'] = str_replace('"','',$tra['Points']);
                    
                    $pct = 0;
                    
                    $tra['iduri'] = "'(".json_encode($iduri).")'";
                    $tra['iduri'] = str_replace('"','',$tra['iduri']);
                    
                    $tra['Cale'] = $this->coords2linestring($puncte);
                    
                    $puncte = array(array(0,0));
                     
                    // resetare variabile
                    $iduri = array();
                    $mergea = false;
                    $distanta = 0;
                    $distanta_rap = 0;
                    $VitMax = 0;
                    $timp_opriri_scurte = 0 ;
                    $timp_fara_semanl = 0;
                    $dist_fara_semanl = 0;
                    $nr_opriri = 0;

                    $key = $key_end;   // sar putin inapoi sa contorizez corect timpul de stationare
                    //    echo "Salvare deplasare $key <br>";
                    //    dump($tra );
                }
                else {  // a primit  comanda de salvare dintr-o stationare trebuie sa incep un alt traseu
                    //$this->Mesaj("Salvare pozitie $key");
                    // caclulez timpul de stationare de la capat
                    $tra['Tst'] = ( $row_fin['DP']  - $row_end['DP']  ) / 60;  // timpul de cand masina stationeaza
                        
                    $tra['Tmot'] = $timp_motor;                // Timp de functionare cu motorul pronit
                    $tra['Trac'] = $timp_racire;              //Timp de functionare termoking
                    $timp_racire = 0;
                    $timp_motor = 0;
                        
                    // aici trebuie sa fac niste verificari sa vad daca traseul este OK.
                    if ($tra['DL'] != $tra['PL']) {
                        $trasee[] = $tra;
                        $mergea = true;
                        $row_start =  $row_fin;
                        $key_start = $key_fin;
                        $key = $key_fin;
                    }
                    else {
                         $this->Mesaj( " Mai bine ne oprim!! :(");
                         break;       
                    }
                    //$distanta = $dist_start; distanta se recaluleaza pentru se reia de la pozitia in care masina a prornit

                    $tra = $this->Init_tra($row_fin);  // initializez un nou traseu
                        
                    //    echo "Salvare stationare $key <br>";
                    //    dump($tra );
                }
                $save = false;
                $posibil_stop = false;
                $posibil_start = false;

            }
            else $key++;  // trec la pozitia urmatoare

            if (sizeof($trasee) == 100) {
                $DataPreluc = $this->Salveaza_Trasee($idm,$trasee);
                $trasee = array(); 
            }
        }



        $end_time = microtime_float();
        $dif_time = round($end_time - $begin_time, 5);
        $this->Mesaj( "<br> Executie in $dif_time secunde");

        $this->Mesaj( "<br> Utmimul traseul procesat este de la  ". $tra['DL'] ." GMT - pana la ". $tra['PL'] ." GMT")  ;

        return $trasee;  // se se returneaza tabelul prelucrat

    }




# LatLon coordinates to MySQL LineString

    function coords2linestring($puncte){
        if (sizeof($puncte) == 0) return "";
        $rez = 'GeomFromText("LINESTRING(';
        foreach ($puncte as $point) {
            $rez = $rez . $point[0] ." ". $point[1].",";
        }
        $rez = substr_replace($rez ,')")',-1);
        return $rez;
    }
    


}

"""
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 