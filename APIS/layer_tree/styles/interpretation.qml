<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" simplifyDrawingTol="1" simplifyMaxScale="1" minScale="1e+08" simplifyDrawingHints="1" version="3.8.3-Zanzibar" styleCategories="AllStyleCategories" labelsEnabled="0" simplifyAlgorithm="0" simplifyLocal="1" hasScaleBasedVisibilityFlag="0" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 symbollevels="0" enableorderby="0" type="singleSymbol" forceraster="0">
    <symbols>
      <symbol clip_to_extent="1" force_rhr="0" type="fill" name="0" alpha="1">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="213,161,230,153"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="168,61,204,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
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
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory penWidth="0" lineSizeScale="3x:0,0,0,0,0,0" minScaleDenominator="0" backgroundColor="#ffffff" scaleBasedVisibility="0" sizeType="MM" enabled="0" penColor="#000000" penAlpha="255" rotationOffset="270" barWidth="5" maxScaleDenominator="1e+08" diagramOrientation="Up" width="15" height="15" lineSizeType="MM" backgroundAlpha="255" sizeScale="3x:0,0,0,0,0,0" opacity="1" scaleDependency="Area" labelPlacementMethod="XHeight" minimumSize="0">
      <fontProperties description="MS Shell Dlg 2,7.875,-1,5,50,0,0,0,0,0" style=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings showAll="1" linePlacementFlags="18" zIndex="0" priority="0" dist="0" placement="1" obstacle="0">
    <properties>
      <Option type="Map">
        <Option value="" type="QString" name="name"/>
        <Option name="properties"/>
        <Option value="collection" type="QString" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="ID">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="INT">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="STRUKTUR">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="FUNDORT">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="LUFTBILD">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="BEARBEITER">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="ID" name=""/>
    <alias index="1" field="INT" name=""/>
    <alias index="2" field="STRUKTUR" name=""/>
    <alias index="3" field="FUNDORT" name=""/>
    <alias index="4" field="LUFTBILD" name=""/>
    <alias index="5" field="BEARBEITER" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" expression="" field="ID"/>
    <default applyOnUpdate="0" expression="" field="INT"/>
    <default applyOnUpdate="0" expression="" field="STRUKTUR"/>
    <default applyOnUpdate="0" expression="" field="FUNDORT"/>
    <default applyOnUpdate="0" expression="" field="LUFTBILD"/>
    <default applyOnUpdate="0" expression="" field="BEARBEITER"/>
  </defaults>
  <constraints>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="ID"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="INT"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="STRUKTUR"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="FUNDORT"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="LUFTBILD"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="BEARBEITER"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="ID"/>
    <constraint exp="" desc="" field="INT"/>
    <constraint exp="" desc="" field="STRUKTUR"/>
    <constraint exp="" desc="" field="FUNDORT"/>
    <constraint exp="" desc="" field="LUFTBILD"/>
    <constraint exp="" desc="" field="BEARBEITER"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" width="-1" name="ID" hidden="0"/>
      <column type="field" width="-1" name="INT" hidden="0"/>
      <column type="field" width="-1" name="STRUKTUR" hidden="0"/>
      <column type="field" width="-1" name="FUNDORT" hidden="0"/>
      <column type="field" width="-1" name="LUFTBILD" hidden="0"/>
      <column type="field" width="-1" name="BEARBEITER" hidden="0"/>
      <column type="actions" width="-1" hidden="1"/>
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
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="BEARBEITER"/>
    <field editable="1" name="FUNDORT"/>
    <field editable="1" name="ID"/>
    <field editable="1" name="INT"/>
    <field editable="1" name="LUFTBILD"/>
    <field editable="1" name="STRUKTUR"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="BEARBEITER"/>
    <field labelOnTop="0" name="FUNDORT"/>
    <field labelOnTop="0" name="ID"/>
    <field labelOnTop="0" name="INT"/>
    <field labelOnTop="0" name="LUFTBILD"/>
    <field labelOnTop="0" name="STRUKTUR"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>ID</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
