<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="100000" simplifyDrawingTol="1" simplifyMaxScale="1" minScale="1e+08" simplifyDrawingHints="1" version="3.8.3-Zanzibar" styleCategories="AllStyleCategories" labelsEnabled="0" simplifyAlgorithm="0" simplifyLocal="1" hasScaleBasedVisibilityFlag="0" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 symbollevels="0" enableorderby="0" type="singleSymbol" forceraster="0">
    <symbols>
      <symbol clip_to_extent="1" force_rhr="0" type="fill" name="0" alpha="1">
        <layer locked="0" class="SimpleLine" enabled="1" pass="0">
          <prop k="capstyle" v="square"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="line_color" v="40,70,200,255"/>
          <prop k="line_style" v="dot"/>
          <prop k="line_width" v="0.4"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0.8"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Pie" attributeLegend="1">
    <DiagramCategory penWidth="0" lineSizeScale="3x:0,0,0,0,0,0" minScaleDenominator="100000" backgroundColor="#ffffff" scaleBasedVisibility="0" sizeType="MM" enabled="0" penColor="#000000" penAlpha="255" rotationOffset="270" barWidth="5" maxScaleDenominator="1e+08" diagramOrientation="Up" width="15" height="15" lineSizeType="MM" backgroundAlpha="255" sizeScale="3x:0,0,0,0,0,0" opacity="1" scaleDependency="Area" labelPlacementMethod="XHeight" minimumSize="0">
      <fontProperties description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0" style=""/>
      <attribute color="#000000" label="" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings showAll="1" linePlacementFlags="2" zIndex="0" priority="0" dist="0" placement="0" obstacle="0">
    <properties>
      <Option type="Map">
        <Option value="" type="QString" name="name"/>
        <Option type="Map" name="properties">
          <Option type="Map" name="show">
            <Option value="true" type="bool" name="active"/>
            <Option value="ogc_fid" type="QString" name="field"/>
            <Option value="2" type="int" name="type"/>
          </Option>
        </Option>
        <Option value="collection" type="QString" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="ogc_fid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="fundortnummer">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="fundstellenummer">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="sicherheit">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="datierung">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="datierung_zeitstufe">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="datierung_periode">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="datierung_periode_detail">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="phase">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="phase_von">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="phase_bis">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="datierungsbasis">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="kultur">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="befundart_detail">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="befundart">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="fundgewinnung_quelle">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="sonstiges">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="erstmeldung_jahr">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="datum_ersteintrag">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="datum_aenderung">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="bdanummer">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="erhaltung">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="bearbeiter">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="datum_abs_1">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="datum_abs_2">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="parzellennummern">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="gkx">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="gky">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="meridian">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="longitude">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="latitude">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="flaeche">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="aktion">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="aktionsdatum">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="aktionsuser">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="befund">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="literatur">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="kommentar_lage">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="fundverbleib">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="befundgeschichte">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="fundbeschreibung">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="common_name">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="flurname">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="ogc_fid" name=""/>
    <alias index="1" field="fundortnummer" name=""/>
    <alias index="2" field="fundstellenummer" name=""/>
    <alias index="3" field="sicherheit" name=""/>
    <alias index="4" field="datierung" name=""/>
    <alias index="5" field="datierung_zeitstufe" name=""/>
    <alias index="6" field="datierung_periode" name=""/>
    <alias index="7" field="datierung_periode_detail" name=""/>
    <alias index="8" field="phase" name=""/>
    <alias index="9" field="phase_von" name=""/>
    <alias index="10" field="phase_bis" name=""/>
    <alias index="11" field="datierungsbasis" name=""/>
    <alias index="12" field="kultur" name=""/>
    <alias index="13" field="befundart_detail" name=""/>
    <alias index="14" field="befundart" name=""/>
    <alias index="15" field="fundgewinnung_quelle" name=""/>
    <alias index="16" field="sonstiges" name=""/>
    <alias index="17" field="erstmeldung_jahr" name=""/>
    <alias index="18" field="datum_ersteintrag" name=""/>
    <alias index="19" field="datum_aenderung" name=""/>
    <alias index="20" field="bdanummer" name=""/>
    <alias index="21" field="erhaltung" name=""/>
    <alias index="22" field="bearbeiter" name=""/>
    <alias index="23" field="datum_abs_1" name=""/>
    <alias index="24" field="datum_abs_2" name=""/>
    <alias index="25" field="parzellennummern" name=""/>
    <alias index="26" field="gkx" name=""/>
    <alias index="27" field="gky" name=""/>
    <alias index="28" field="meridian" name=""/>
    <alias index="29" field="longitude" name=""/>
    <alias index="30" field="latitude" name=""/>
    <alias index="31" field="flaeche" name=""/>
    <alias index="32" field="aktion" name=""/>
    <alias index="33" field="aktionsdatum" name=""/>
    <alias index="34" field="aktionsuser" name=""/>
    <alias index="35" field="befund" name=""/>
    <alias index="36" field="literatur" name=""/>
    <alias index="37" field="kommentar_lage" name=""/>
    <alias index="38" field="fundverbleib" name=""/>
    <alias index="39" field="befundgeschichte" name=""/>
    <alias index="40" field="fundbeschreibung" name=""/>
    <alias index="41" field="common_name" name=""/>
    <alias index="42" field="flurname" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" expression="" field="ogc_fid"/>
    <default applyOnUpdate="0" expression="" field="fundortnummer"/>
    <default applyOnUpdate="0" expression="" field="fundstellenummer"/>
    <default applyOnUpdate="0" expression="" field="sicherheit"/>
    <default applyOnUpdate="0" expression="" field="datierung"/>
    <default applyOnUpdate="0" expression="" field="datierung_zeitstufe"/>
    <default applyOnUpdate="0" expression="" field="datierung_periode"/>
    <default applyOnUpdate="0" expression="" field="datierung_periode_detail"/>
    <default applyOnUpdate="0" expression="" field="phase"/>
    <default applyOnUpdate="0" expression="" field="phase_von"/>
    <default applyOnUpdate="0" expression="" field="phase_bis"/>
    <default applyOnUpdate="0" expression="" field="datierungsbasis"/>
    <default applyOnUpdate="0" expression="" field="kultur"/>
    <default applyOnUpdate="0" expression="" field="befundart_detail"/>
    <default applyOnUpdate="0" expression="" field="befundart"/>
    <default applyOnUpdate="0" expression="" field="fundgewinnung_quelle"/>
    <default applyOnUpdate="0" expression="" field="sonstiges"/>
    <default applyOnUpdate="0" expression="" field="erstmeldung_jahr"/>
    <default applyOnUpdate="0" expression="" field="datum_ersteintrag"/>
    <default applyOnUpdate="0" expression="" field="datum_aenderung"/>
    <default applyOnUpdate="0" expression="" field="bdanummer"/>
    <default applyOnUpdate="0" expression="" field="erhaltung"/>
    <default applyOnUpdate="0" expression="" field="bearbeiter"/>
    <default applyOnUpdate="0" expression="" field="datum_abs_1"/>
    <default applyOnUpdate="0" expression="" field="datum_abs_2"/>
    <default applyOnUpdate="0" expression="" field="parzellennummern"/>
    <default applyOnUpdate="0" expression="" field="gkx"/>
    <default applyOnUpdate="0" expression="" field="gky"/>
    <default applyOnUpdate="0" expression="" field="meridian"/>
    <default applyOnUpdate="0" expression="" field="longitude"/>
    <default applyOnUpdate="0" expression="" field="latitude"/>
    <default applyOnUpdate="0" expression="" field="flaeche"/>
    <default applyOnUpdate="0" expression="" field="aktion"/>
    <default applyOnUpdate="0" expression="" field="aktionsdatum"/>
    <default applyOnUpdate="0" expression="" field="aktionsuser"/>
    <default applyOnUpdate="0" expression="" field="befund"/>
    <default applyOnUpdate="0" expression="" field="literatur"/>
    <default applyOnUpdate="0" expression="" field="kommentar_lage"/>
    <default applyOnUpdate="0" expression="" field="fundverbleib"/>
    <default applyOnUpdate="0" expression="" field="befundgeschichte"/>
    <default applyOnUpdate="0" expression="" field="fundbeschreibung"/>
    <default applyOnUpdate="0" expression="" field="common_name"/>
    <default applyOnUpdate="0" expression="" field="flurname"/>
  </defaults>
  <constraints>
    <constraint unique_strength="1" constraints="3" exp_strength="0" notnull_strength="1" field="ogc_fid"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="fundortnummer"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="fundstellenummer"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="sicherheit"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="datierung"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="datierung_zeitstufe"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="datierung_periode"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="datierung_periode_detail"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="phase"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="phase_von"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="phase_bis"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="datierungsbasis"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="kultur"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="befundart_detail"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="befundart"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="fundgewinnung_quelle"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="sonstiges"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="erstmeldung_jahr"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="datum_ersteintrag"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="datum_aenderung"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="bdanummer"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="erhaltung"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="bearbeiter"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="datum_abs_1"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="datum_abs_2"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="parzellennummern"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="gkx"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="gky"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="meridian"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="longitude"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="latitude"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="flaeche"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="aktion"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="aktionsdatum"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="aktionsuser"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="befund"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="literatur"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="kommentar_lage"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="fundverbleib"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="befundgeschichte"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="fundbeschreibung"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="common_name"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="flurname"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="ogc_fid"/>
    <constraint exp="" desc="" field="fundortnummer"/>
    <constraint exp="" desc="" field="fundstellenummer"/>
    <constraint exp="" desc="" field="sicherheit"/>
    <constraint exp="" desc="" field="datierung"/>
    <constraint exp="" desc="" field="datierung_zeitstufe"/>
    <constraint exp="" desc="" field="datierung_periode"/>
    <constraint exp="" desc="" field="datierung_periode_detail"/>
    <constraint exp="" desc="" field="phase"/>
    <constraint exp="" desc="" field="phase_von"/>
    <constraint exp="" desc="" field="phase_bis"/>
    <constraint exp="" desc="" field="datierungsbasis"/>
    <constraint exp="" desc="" field="kultur"/>
    <constraint exp="" desc="" field="befundart_detail"/>
    <constraint exp="" desc="" field="befundart"/>
    <constraint exp="" desc="" field="fundgewinnung_quelle"/>
    <constraint exp="" desc="" field="sonstiges"/>
    <constraint exp="" desc="" field="erstmeldung_jahr"/>
    <constraint exp="" desc="" field="datum_ersteintrag"/>
    <constraint exp="" desc="" field="datum_aenderung"/>
    <constraint exp="" desc="" field="bdanummer"/>
    <constraint exp="" desc="" field="erhaltung"/>
    <constraint exp="" desc="" field="bearbeiter"/>
    <constraint exp="" desc="" field="datum_abs_1"/>
    <constraint exp="" desc="" field="datum_abs_2"/>
    <constraint exp="" desc="" field="parzellennummern"/>
    <constraint exp="" desc="" field="gkx"/>
    <constraint exp="" desc="" field="gky"/>
    <constraint exp="" desc="" field="meridian"/>
    <constraint exp="" desc="" field="longitude"/>
    <constraint exp="" desc="" field="latitude"/>
    <constraint exp="" desc="" field="flaeche"/>
    <constraint exp="" desc="" field="aktion"/>
    <constraint exp="" desc="" field="aktionsdatum"/>
    <constraint exp="" desc="" field="aktionsuser"/>
    <constraint exp="" desc="" field="befund"/>
    <constraint exp="" desc="" field="literatur"/>
    <constraint exp="" desc="" field="kommentar_lage"/>
    <constraint exp="" desc="" field="fundverbleib"/>
    <constraint exp="" desc="" field="befundgeschichte"/>
    <constraint exp="" desc="" field="fundbeschreibung"/>
    <constraint exp="" desc="" field="common_name"/>
    <constraint exp="" desc="" field="flurname"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" width="-1" name="fundortnummer" hidden="0"/>
      <column type="field" width="-1" name="fundstellenummer" hidden="0"/>
      <column type="field" width="-1" name="sicherheit" hidden="0"/>
      <column type="field" width="-1" name="datierung" hidden="0"/>
      <column type="field" width="-1" name="datierung_periode" hidden="0"/>
      <column type="field" width="-1" name="datierung_periode_detail" hidden="0"/>
      <column type="field" width="-1" name="phase" hidden="0"/>
      <column type="field" width="-1" name="phase_von" hidden="0"/>
      <column type="field" width="-1" name="phase_bis" hidden="0"/>
      <column type="field" width="-1" name="datierungsbasis" hidden="0"/>
      <column type="field" width="-1" name="kultur" hidden="0"/>
      <column type="field" width="-1" name="fundgewinnung_quelle" hidden="0"/>
      <column type="field" width="-1" name="sonstiges" hidden="0"/>
      <column type="field" width="-1" name="erstmeldung_jahr" hidden="0"/>
      <column type="field" width="-1" name="datum_ersteintrag" hidden="0"/>
      <column type="field" width="-1" name="datum_aenderung" hidden="0"/>
      <column type="field" width="-1" name="bdanummer" hidden="0"/>
      <column type="field" width="-1" name="erhaltung" hidden="0"/>
      <column type="field" width="-1" name="bearbeiter" hidden="0"/>
      <column type="field" width="-1" name="datum_abs_1" hidden="0"/>
      <column type="field" width="-1" name="datum_abs_2" hidden="0"/>
      <column type="field" width="-1" name="parzellennummern" hidden="0"/>
      <column type="field" width="-1" name="gkx" hidden="0"/>
      <column type="field" width="-1" name="gky" hidden="0"/>
      <column type="field" width="-1" name="meridian" hidden="0"/>
      <column type="field" width="-1" name="longitude" hidden="0"/>
      <column type="field" width="-1" name="latitude" hidden="0"/>
      <column type="field" width="-1" name="flaeche" hidden="0"/>
      <column type="field" width="-1" name="aktion" hidden="0"/>
      <column type="field" width="-1" name="aktionsdatum" hidden="0"/>
      <column type="field" width="-1" name="aktionsuser" hidden="0"/>
      <column type="field" width="-1" name="befund" hidden="0"/>
      <column type="field" width="-1" name="literatur" hidden="0"/>
      <column type="field" width="-1" name="kommentar_lage" hidden="0"/>
      <column type="field" width="-1" name="fundverbleib" hidden="0"/>
      <column type="field" width="-1" name="fundbeschreibung" hidden="0"/>
      <column type="actions" width="-1" hidden="1"/>
      <column type="field" width="-1" name="ogc_fid" hidden="0"/>
      <column type="field" width="-1" name="datierung_zeitstufe" hidden="0"/>
      <column type="field" width="-1" name="befundart_detail" hidden="0"/>
      <column type="field" width="-1" name="befundart" hidden="0"/>
      <column type="field" width="-1" name="befundgeschichte" hidden="0"/>
      <column type="field" width="-1" name="common_name" hidden="0"/>
      <column type="field" width="-1" name="flurname" hidden="0"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from PyQt4.QtGui import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="aktion"/>
    <field editable="1" name="aktionsdatum"/>
    <field editable="1" name="aktionsuser"/>
    <field editable="1" name="bdanummer"/>
    <field editable="1" name="bearbeiter"/>
    <field editable="1" name="befund"/>
    <field editable="1" name="befundart"/>
    <field editable="1" name="befundart_detail"/>
    <field editable="1" name="befundgeschichte"/>
    <field editable="1" name="common_name"/>
    <field editable="1" name="datierung"/>
    <field editable="1" name="datierung_periode"/>
    <field editable="1" name="datierung_periode_detail"/>
    <field editable="1" name="datierung_zeitstufe"/>
    <field editable="1" name="datierungsbasis"/>
    <field editable="1" name="datum_abs_1"/>
    <field editable="1" name="datum_abs_2"/>
    <field editable="1" name="datum_aenderung"/>
    <field editable="1" name="datum_ersteintrag"/>
    <field editable="1" name="erhaltung"/>
    <field editable="1" name="erstmeldung_jahr"/>
    <field editable="1" name="flaeche"/>
    <field editable="1" name="flurname"/>
    <field editable="1" name="fundbeschreibung"/>
    <field editable="1" name="fundgewinnung_quelle"/>
    <field editable="1" name="fundortnummer"/>
    <field editable="1" name="fundstellenummer"/>
    <field editable="1" name="fundverbleib"/>
    <field editable="1" name="gkx"/>
    <field editable="1" name="gky"/>
    <field editable="1" name="kommentar_lage"/>
    <field editable="1" name="kultur"/>
    <field editable="1" name="latitude"/>
    <field editable="1" name="literatur"/>
    <field editable="1" name="longitude"/>
    <field editable="1" name="meridian"/>
    <field editable="1" name="ogc_fid"/>
    <field editable="1" name="parzellennummern"/>
    <field editable="1" name="phase"/>
    <field editable="1" name="phase_bis"/>
    <field editable="1" name="phase_von"/>
    <field editable="1" name="sicherheit"/>
    <field editable="1" name="sonstiges"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="aktion"/>
    <field labelOnTop="0" name="aktionsdatum"/>
    <field labelOnTop="0" name="aktionsuser"/>
    <field labelOnTop="0" name="bdanummer"/>
    <field labelOnTop="0" name="bearbeiter"/>
    <field labelOnTop="0" name="befund"/>
    <field labelOnTop="0" name="befundart"/>
    <field labelOnTop="0" name="befundart_detail"/>
    <field labelOnTop="0" name="befundgeschichte"/>
    <field labelOnTop="0" name="common_name"/>
    <field labelOnTop="0" name="datierung"/>
    <field labelOnTop="0" name="datierung_periode"/>
    <field labelOnTop="0" name="datierung_periode_detail"/>
    <field labelOnTop="0" name="datierung_zeitstufe"/>
    <field labelOnTop="0" name="datierungsbasis"/>
    <field labelOnTop="0" name="datum_abs_1"/>
    <field labelOnTop="0" name="datum_abs_2"/>
    <field labelOnTop="0" name="datum_aenderung"/>
    <field labelOnTop="0" name="datum_ersteintrag"/>
    <field labelOnTop="0" name="erhaltung"/>
    <field labelOnTop="0" name="erstmeldung_jahr"/>
    <field labelOnTop="0" name="flaeche"/>
    <field labelOnTop="0" name="flurname"/>
    <field labelOnTop="0" name="fundbeschreibung"/>
    <field labelOnTop="0" name="fundgewinnung_quelle"/>
    <field labelOnTop="0" name="fundortnummer"/>
    <field labelOnTop="0" name="fundstellenummer"/>
    <field labelOnTop="0" name="fundverbleib"/>
    <field labelOnTop="0" name="gkx"/>
    <field labelOnTop="0" name="gky"/>
    <field labelOnTop="0" name="kommentar_lage"/>
    <field labelOnTop="0" name="kultur"/>
    <field labelOnTop="0" name="latitude"/>
    <field labelOnTop="0" name="literatur"/>
    <field labelOnTop="0" name="longitude"/>
    <field labelOnTop="0" name="meridian"/>
    <field labelOnTop="0" name="ogc_fid"/>
    <field labelOnTop="0" name="parzellennummern"/>
    <field labelOnTop="0" name="phase"/>
    <field labelOnTop="0" name="phase_bis"/>
    <field labelOnTop="0" name="phase_von"/>
    <field labelOnTop="0" name="sicherheit"/>
    <field labelOnTop="0" name="sonstiges"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>meridian</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
