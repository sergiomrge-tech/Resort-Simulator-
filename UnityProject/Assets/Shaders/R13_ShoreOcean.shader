Shader "Resort/R13/ShoreOcean" {
 Properties {
  _DeepColor("Deep sea",Color)=(.018,.12,.19,1)
  _ShallowColor("Coastal sea",Color)=(.065,.30,.29,1)
  _Smoothness("Water smoothness",Range(0,1))=.78
  _Speed("Swell speed",Range(0,2))=.32
 }
 SubShader {
  Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" "Queue"="Geometry"}
  Pass {
   Tags {"LightMode"="UniversalForward"}
   Cull Back ZWrite On
   HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #pragma multi_compile_fog
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
   CBUFFER_START(UnityPerMaterial)
    float4 _DeepColor,_ShallowColor;
    float _Smoothness,_Speed;
   CBUFFER_END
   struct A {float4 positionOS:POSITION;float2 uv:TEXCOORD0;};
   struct V {float4 positionCS:SV_POSITION;float3 world:TEXCOORD0;float2 shore:TEXCOORD1;float fog:TEXCOORD2;};
   V vert(A a){V o;VertexPositionInputs p=GetVertexPositionInputs(a.positionOS.xyz);o.positionCS=p.positionCS;o.world=p.positionWS;o.shore=a.uv;o.fog=ComputeFogFactor(p.positionCS.z);return o;}
   half4 frag(V v):SV_Target {
    // OSM-relative metres in UV0: waves approach the coast across its real curve.
    float x=v.shore.x,d=-v.shore.y,t=_Time.y*_Speed;
    float p=d*.55+t*1.35+.30*sin(x*.037);
    float q=d*1.17+t*.73+x*.071;
    float r=d*2.51+t*1.91-x*.113;
    float2 slope=float2(.010*cos(p)*cos(x*.037)+.014*cos(q)-.008*cos(r),.055*cos(p)+.025*cos(q)+.018*cos(r));
    float3 along=float3(.694658,0,-.719340),inland=float3(-.719340,0,-.694658);
    float3 n=normalize(float3(0,1,0)+along*slope.x+inland*slope.y);
    float3 view=SafeNormalize(_WorldSpaceCameraPos-v.world);
    Light light=GetMainLight();float ndl=saturate(dot(n,light.direction));
    float fresnel=.02+.98*pow(1-saturate(dot(n,view)),5);
    float3 col=lerp(_ShallowColor.rgb,_DeepColor.rgb,saturate(d/65));
    col*=.52+.48*ndl;
    float3 sky=SampleSH(reflect(-view,n));
    col=lerp(col,max(sky,0),fresnel*.65);
    float spec=pow(saturate(dot(n,SafeNormalize(light.direction+view))),lerp(32,220,_Smoothness));
    col+=light.color*spec*.28;
    float breaking=pow(saturate(.5+.5*sin(p)),18)*exp(-d*.32);
    float shorewash=(.5+.5*sin(t*1.35+x*.017))*exp(-d*1.3);
    col=lerp(col,float3(.64,.73,.69),saturate(breaking*.5+shorewash*.2));
    return half4(MixFog(col,v.fog),1);
   }
   ENDHLSL
  }
 }
}
