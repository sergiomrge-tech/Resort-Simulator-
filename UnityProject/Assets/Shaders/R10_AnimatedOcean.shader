Shader "Resort/R10/AnimatedOcean"
{
 Properties {
  _DeepColor ("Deep sea", Color) = (0.025,0.16,0.27,1)
  _ShallowColor ("Illuminated swell", Color) = (0.095,0.39,0.53,1)
  _FoamColor ("Reflected surf", Color) = (.52,.77,.82,1)
  _WaveSpeed ("Wave speed", Range(0,3)) = .36
  _WaveContrast ("Glint strength", Range(0,1)) = .36
 }
 SubShader {
  Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" "Queue"="Geometry" }
  Pass {
   Name "AnimatedOcean"
   Tags { "LightMode"="UniversalForward" }
   ZWrite On
   Cull Off
   HLSLPROGRAM
   #pragma vertex OceanVert
   #pragma fragment OceanFrag
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   CBUFFER_START(UnityPerMaterial)
    float4 _DeepColor,_ShallowColor,_FoamColor;
    float _WaveSpeed,_WaveContrast;
   CBUFFER_END
   struct Attributes { float4 positionOS : POSITION; };
   struct Varyings { float4 positionCS : SV_POSITION; float3 positionWS : TEXCOORD0; };
   Varyings OceanVert(Attributes input) {
    Varyings v;
    VertexPositionInputs p=GetVertexPositionInputs(input.positionOS.xyz);
    v.positionCS=p.positionCS;
    v.positionWS=p.positionWS;
    return v;
   }
   half4 OceanFrag(Varyings v):SV_Target {
    float2 p=v.positionWS.xz;
    float t=_Time.y*_WaveSpeed;
    float s1=sin(p.x*.029+p.y*.039-t*1.8);
    float s2=sin(p.x*.066-p.y*.034+t);
    float s3=sin(p.x*.14+p.y*.085-t*2.9);
    float mixv=saturate(.48+.22*s1+.21*s2+.09*s3);
    float3 c=lerp(_DeepColor.rgb,_ShallowColor.rgb,lerp(.15,.85,mixv));
    float crest=smoothstep(.87,.99,.58+.26*s1+.20*s2);
    c=lerp(c,_FoamColor.rgb,crest*.16*_WaveContrast);
    float angle=saturate(dot(normalize(_WorldSpaceCameraPos-v.positionWS),float3(0,1,0)));
    c*=lerp(.82,1.06,angle);
    return half4(c,1);
   }
   ENDHLSL
  }
 }
 FallBack "Universal Render Pipeline/Unlit"
}
