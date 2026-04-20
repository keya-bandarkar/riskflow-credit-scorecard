"""
Export Architecture Diagrams to PNG format
Converts Mermaid diagrams to PNG images using mermaid-cli
"""

import subprocess
import os
from pathlib import Path

# Define all diagrams
DIAGRAMS = {
    "1_detailed_system_architecture.mmd": """graph TB
    subgraph DataLayer["📊 Data Layer"]
        German["German Credit Dataset<br/>1000 samples"]
        Australian["Australian Credit Dataset<br/>690 samples"]
        Japanese["Japanese Credit Dataset<br/>690 samples"]
    end
    
    subgraph PreprocessingLayer["⚙️ Preprocessing & Feature Engineering"]
        Loading["Data Loading &<br/>Integration"]
        Cleaning["Data Cleaning<br/>& Validation"]
        WOE["WOE/IV Transformation<br/>Feature Engineering"]
        Binning["Feature Binning<br/>& Encoding"]
    end
    
    subgraph ModelLayer["🧠 Model Layer"]
        LR["Logistic Regression<br/>Max: 99.65% AUC"]
        RF["Random Forest<br/>Max: 99.14% AUC"]
        XGB["XGBoost<br/>Max: 99.07% AUC"]
        LGB["LightGBM<br/>Max: 99.21% AUC"]
    end
    
    subgraph EvaluationLayer["📈 Evaluation Layer"]
        Metrics["Model Metrics<br/>Accuracy, AUC, KS"]
        Comparison["Model Comparison<br/>& Selection"]
        Validation["Cross-Validation<br/>& Testing"]
    end
    
    subgraph ScorecardLayer["📋 Scorecard Layer"]
        Scaling["Score Scaling<br/>Factor & Offset"]
        Mapping["WOE to Score<br/>Mapping"]
        Generation["Scorecard CSV<br/>Generation"]
    end
    
    subgraph ApplicationLayer["🌐 Web Application Layer"]
        API["Flask REST API<br/>/config, /calculate"]
        WebApp["Frontend<br/>HTML/CSS/JS"]
        Cache["Scorecard Cache<br/>final_scorecard.csv"]
    end
    
    subgraph OutputLayer["📤 Output Layer"]
        Plots["Visualization<br/>ROC, Distribution, Importance"]
        Logs["Evaluation Logs<br/>& Reports"]
        Repo["GitHub Repository<br/>Version Control"]
    end
    
    German --> Loading
    Australian --> Loading
    Japanese --> Loading
    
    Loading --> Cleaning
    Cleaning --> WOE
    WOE --> Binning
    
    Binning --> LR
    Binning --> RF
    Binning --> XGB
    Binning --> LGB
    
    LR --> Metrics
    RF --> Metrics
    XGB --> Metrics
    LGB --> Metrics
    
    Metrics --> Comparison
    Comparison --> Validation
    
    Validation --> Scaling
    Scaling --> Mapping
    Mapping --> Generation
    
    Generation --> Cache
    Cache --> API
    Cache --> WebApp
    
    LR --> Plots
    Metrics --> Plots
    Validation --> Logs
    Plots --> Repo
    Logs --> Repo
    
    API --> WebApp""",
    
    "2_component_interaction.mmd": """graph TB
    subgraph Client["Client Layer"]
        Browser["Web Browser<br/>User Interface"]
        HTMLForm["HTML Form<br/>Applicant Input"]
    end
    
    subgraph Web["Web Framework"]
        FlaskServer["Flask Server<br/>Port 5000"]
        ConfigRoute["GET /config<br/>Return Scorecard"]
        CalcRoute["POST /calculate<br/>Score Applicant"]
        JsonResp["JSON Response<br/>Score + Risk"]
    end
    
    subgraph Processing["Processing Engine"]
        FeatureLookup["Feature Lookup<br/>Input Validation"]
        BinAssignment["Bin Assignment<br/>Feature Values"]
        WOETransform["WOE Transform<br/>Score Lookup"]
        ScoreAgg["Score Aggregation<br/>Sum Contributions"]
    end
    
    subgraph DataStore["Data Storage"]
        ScorecardCSV["final_scorecard.csv<br/>Pre-computed Scores"]
        InMemCache["In-Memory Cache<br/>Pandas DataFrame"]
        ConfigJSON["Config JSON<br/>Feature Metadata"]
    end
    
    subgraph ML["ML Pipeline"]
        Preprocessing["Preprocessing<br/>Data Cleaning"]
        FeatureEng["Feature Engineering<br/>WOE/IV Computation"]
        ModelTraining["Model Training<br/>4 Models"]
        Evaluation["Model Evaluation<br/>Cross-Validation"]
        Selection["Model Selection<br/>Best Performer"]
    end
    
    subgraph Visualization["Visualization & Analysis"]
        ROCPlot["ROC Curve Plot<br/>Model Performance"]
        DistPlot["Score Distribution<br/>Good vs Bad"]
        FeaturePlot["Feature Importance<br/>IV Ranking"]
        ComparisonPlot["Model Comparison<br/>AUC Bar Chart"]
        WOEPlot["WOE Transformation<br/>Top Features"]
    end
    
    subgraph Version["Version Control"]
        GitRepo["GitHub Repository<br/>riskflow-credit-scorecard"]
        Commits["Code & Data<br/>Version History"]
    end
    
    Browser -->|Input Data| HTMLForm
    HTMLForm -->|JavaScript| FlaskServer
    
    FlaskServer -->|Route Request| ConfigRoute
    FlaskServer -->|Route Request| CalcRoute
    
    ConfigRoute -->|Read| InMemCache
    ConfigRoute -->|Return| JsonResp
    
    CalcRoute -->|Process| FeatureLookup
    FeatureLookup -->|Assign| BinAssignment
    BinAssignment -->|Lookup| InMemCache
    InMemCache -->|WOE Values| WOETransform
    WOETransform -->|Aggregate| ScoreAgg
    ScoreAgg -->|Calculate Risk| JsonResp
    
    JsonResp -->|Display| Browser
    
    ScorecardCSV -->|Load on Start| InMemCache
    ConfigJSON -->|Load on Start| InMemCache
    
    Preprocessing -->|Output| FeatureEng
    FeatureEng -->|Output| ModelTraining
    ModelTraining -->|Evaluate| Evaluation
    Evaluation -->|Compare| Selection
    Selection -->|Generate| ScorecardCSV
    Selection -->|Config| ConfigJSON
    
    Selection -->|Model Results| ROCPlot
    Selection -->|Scores| DistPlot
    FeatureEng -->|IV Values| FeaturePlot
    Evaluation -->|Metrics| ComparisonPlot
    FeatureEng -->|WOE Bins| WOEPlot
    
    ROCPlot -->|Save| GitRepo
    DistPlot -->|Save| GitRepo
    FeaturePlot -->|Save| GitRepo
    ComparisonPlot -->|Save| GitRepo
    WOEPlot -->|Save| GitRepo
    
    ScorecardCSV -->|Commit| GitRepo
    ConfigJSON -->|Commit| GitRepo
    Selection -->|Code| Commits""",
    
    "3_deployment_architecture.mmd": """graph TB
    subgraph User["End User"]
        User1["👤 User/Administrator<br/>Local Machine"]
    end
    
    subgraph Local["Local Development Environment"]
        CodeEditor["VS Code<br/>Python IDE"]
        Scripts["Python Scripts<br/>Training & Evaluation"]
        VirtualEnv["Python 3.14<br/>Virtual Environment"]
    end
    
    subgraph Training["Training Pipeline<br/>Local Execution"]
        DataDownload["Download Datasets<br/>3 Sources"]
        Preprocess["Preprocessing<br/>german_credit_scorecard.py"]
        TrainModels["Train 4 Models<br/>Individual Scripts"]
        Evaluate["Evaluate & Compare<br/>Model Metrics"]
        Generate["Generate Scorecard<br/>final_scorecard.csv"]
    end
    
    subgraph LocalApp["Local Flask Application"]
        FlaskDev["Flask Development Server<br/>Port 5000<br/>Localhost:5000"]
        StaticFiles["Static Assets<br/>CSS, JavaScript"]
        Templates["HTML Templates<br/>User Interface"]
    end
    
    subgraph Browser["Web Browser"]
        UI["Credit Scorecard UI<br/>Real-time Scoring"]
    end
    
    subgraph DataDir["Local File System"]
        ScorecardFile["final_scorecard.csv<br/>Pre-computed Scores"]
        DataFile["german_credit_data.csv<br/>Reference Data"]
        PlotFiles["Visualization Files<br/>PNG Plots"]
    end
    
    subgraph GitHub["GitHub Repository"]
        RepoCode["Source Code<br/>*.py files"]
        RepoData["Scorecard CSV<br/>Model Data"]
        RepoPlots["Visualization Plots<br/>Analysis Charts"]
        RepoDocs["Documentation<br/>README, Architecture"]
        RepoReq["Dependencies<br/>requirements.txt"]
    end
    
    subgraph Version["Version Control"]
        GitLocal["Local Git<br/>.git folder"]
        GitRemote["GitHub Remote<br/>Origin"]
    end
    
    subgraph Deployment["Deployment Ready<br/>Production Setup"]
        Docker["Docker Container<br/>Containerized App"]
        Gunicorn["Gunicorn WSGI<br/>Application Server"]
        Nginx["Nginx Web Server<br/>Reverse Proxy"]
        Database["Optional Database<br/>Audit Logs"]
    end
    
    User1 --> CodeEditor
    CodeEditor --> Scripts
    Scripts --> VirtualEnv
    
    VirtualEnv --> DataDownload
    DataDownload --> Preprocess
    Preprocess --> TrainModels
    TrainModels --> Evaluate
    Evaluate --> Generate
    
    Generate --> ScorecardFile
    Generate --> DataFile
    Evaluate --> PlotFiles
    
    ScorecardFile --> FlaskDev
    StaticFiles --> FlaskDev
    Templates --> FlaskDev
    
    FlaskDev --> UI
    UI -->|HTTP Requests| FlaskDev
    
    Scripts -->|Commit| GitLocal
    ScorecardFile -->|Commit| GitLocal
    PlotFiles -->|Commit| GitLocal
    
    GitLocal -->|Push| GitRemote
    
    RepoCode --> Docker
    RepoData --> Docker
    RepoReq --> Docker
    
    Docker --> Gunicorn
    Gunicorn --> Nginx
    Nginx --> User1
    
    Database -->|Audit Trail| Gunicorn""",
    
    "4_data_flow.mmd": """graph LR
    subgraph InputData["Input Data"]
        Dataset1["German Credit<br/>1,000 rows"]
        Dataset2["Australian Credit<br/>690 rows"]
        Dataset3["Japanese Credit<br/>690 rows"]
    end
    
    subgraph DataIntegration["Integration"]
        Merge["Merge & Align<br/>Features"]
        Combined["Combined Data<br/>2,380 rows<br/>20 features"]
    end
    
    subgraph DataQuality["Quality Control"]
        Missing["Handle Missing<br/>Values"]
        Outliers["Detect Outliers<br/>& Anomalies"]
        Validation["Validate Data<br/>Ranges"]
    end
    
    subgraph SplitData["Data Partitioning"]
        TrainSet["Training Set<br/>70% = 1,666 rows"]
        TestSet["Test Set<br/>30% = 714 rows"]
    end
    
    subgraph FeatureTransform["Feature Engineering"]
        Discrete["Discretize<br/>Continuous Features"]
        CalcWOE["Calculate WOE<br/>Log Odds Ratio"]
        CalcIV["Calculate IV<br/>Information Value"]
        EncodedSet["Encoded Features<br/>WOE Values"]
    end
    
    subgraph ModelTraining["Model Training"]
        TrainLR["Train LR<br/>Logistic Regression"]
        TrainRF["Train RF<br/>Random Forest"]
        TrainXGB["Train XGB<br/>XGBoost"]
        TrainLGB["Train LGB<br/>LightGBM"]
    end
    
    subgraph Prediction["Predictions"]
        PredLR["LR Predictions<br/>Probabilities"]
        PredRF["RF Predictions<br/>Probabilities"]
        PredXGB["XGB Predictions<br/>Probabilities"]
        PredLGB["LGB Predictions<br/>Probabilities"]
    end
    
    subgraph ModelEval["Model Evaluation"]
        MetricsLR["LR Metrics<br/>AUC=99.65%"]
        MetricsRF["RF Metrics<br/>AUC=99.14%"]
        MetricsXGB["XGB Metrics<br/>AUC=99.07%"]
        MetricsLGB["LGB Metrics<br/>AUC=99.21%"]
    end
    
    subgraph Selection["Selection"]
        BestModel["Best: Logistic Regression<br/>AUC=99.65%"]
    end
    
    subgraph ScorecardGen["Scorecard Generation"]
        ExtractCoef["Extract Coefficients<br/>Intercept = 2.814"]
        BinScores["Compute Bin Scores<br/>WOE × Coefficient"]
        ScaleFinal["Scale to 300-850<br/>PDO=28.85, Offset=487.12"]
        FinalCard["Final Scorecard<br/>Variable, Bin, Score"]
    end
    
    subgraph Deployment["Deployment"]
        SaveCSV["Save as CSV<br/>final_scorecard.csv"]
        LoadApp["Load in Flask App<br/>In-Memory Cache"]
    end
    
    subgraph Runtime["Runtime Scoring"]
        UserInput["User Input<br/>Applicant Features"]
        MapBins["Map to Bins<br/>Feature Values"]
        LookupWOE["Lookup WOE<br/>From Scorecard"]
        SumScore["Sum Score<br/>Contributions"]
        RiskLevel["Assign Risk<br/>Good/Fair/Poor"]
    end
    
    subgraph Output["Output"]
        ScoreResult["Return Score<br/>300-850"]
        RiskResult["Return Risk Level<br/>JSON Response"]
    end
    
    Dataset1 --> Merge
    Dataset2 --> Merge
    Dataset3 --> Merge
    
    Merge --> Combined
    Combined --> Missing
    Missing --> Outliers
    Outliers --> Validation
    
    Validation --> TrainSet
    Validation --> TestSet
    
    TrainSet --> Discrete
    Discrete --> CalcWOE
    CalcWOE --> CalcIV
    CalcIV --> EncodedSet
    
    EncodedSet --> TrainLR
    EncodedSet --> TrainRF
    EncodedSet --> TrainXGB
    EncodedSet --> TrainLGB
    
    TestSet --> PredLR
    TestSet --> PredRF
    TestSet --> PredXGB
    TestSet --> PredLGB
    
    TrainLR --> PredLR
    TrainRF --> PredRF
    TrainXGB --> PredXGB
    TrainLGB --> PredLGB
    
    PredLR --> MetricsLR
    PredRF --> MetricsRF
    PredXGB --> MetricsXGB
    PredLGB --> MetricsLGB
    
    MetricsLR --> BestModel
    MetricsRF --> BestModel
    MetricsXGB --> BestModel
    MetricsLGB --> BestModel
    
    BestModel --> ExtractCoef
    EncodedSet --> ExtractCoef
    ExtractCoef --> BinScores
    BinScores --> ScaleFinal
    ScaleFinal --> FinalCard
    
    FinalCard --> SaveCSV
    SaveCSV --> LoadApp
    
    UserInput --> MapBins
    LoadApp --> LookupWOE
    MapBins --> LookupWOE
    LookupWOE --> SumScore
    SumScore --> RiskLevel
    
    RiskLevel --> ScoreResult
    RiskLevel --> RiskResult
    
    ScoreResult --> Output
    RiskResult --> Output""",
    
    "5_components_dependencies.mmd": """graph TB
    subgraph Core["Core System Components"]
        direction TB
        
        subgraph DataSrc["Data Sources"]
            GermanURL["🔗 German Credit URL"]
            AustralianURL["🔗 Australian Credit URL"]
            JapaneseURL["🔗 Japanese Credit URL"]
        end
        
        subgraph PreProc["Preprocessing Module"]
            LoadData["load_data_from_urls"]
            CleanData["clean_and_validate"]
            MergeDatasets["merge_datasets"]
            HandleMissing["handle_missing_values"]
        end
        
        subgraph FeatEng["Feature Engineering"]
            ComputeWOE["compute_woe<br/>Weight of Evidence"]
            ComputeIV["compute_iv<br/>Information Value"]
            BinFeatures["bin_features<br/>Discretization"]
            EncodeFeatures["encode_woe<br/>WOE Mapping"]
        end
        
        subgraph Models["Model Components"]
            LogRegModel["LogisticRegression<br/>Model"]
            RFModel["RandomForestClassifier<br/>Model"]
            XGBModel["XGBClassifier<br/>Model"]
            LGBModel["LGBMClassifier<br/>Model"]
        end
        
        subgraph Eval["Evaluation Module"]
            CalcMetrics["calculate_metrics<br/>AUC, Acc, KS"]
            CompareModels["compare_models<br/>Ranking"]
            SelectBest["select_best_model<br/>Optimization"]
        end
        
        subgraph Scorecard["Scorecard Module"]
            GenScorecard["generate_scorecard<br/>WOE to Score"]
            ScaleScores["scale_scores<br/>PDO & Offset"]
            SaveScorecard["save_to_csv<br/>final_scorecard.csv"]
        end
        
        subgraph Viz["Visualization Module"]
            PlotROC["plot_roc_curve"]
            PlotDist["plot_score_distribution"]
            PlotFeatures["plot_feature_importance"]
            PlotComparison["plot_model_comparison"]
            PlotWOE["plot_woe_features"]
        end
    end
    
    subgraph AppLayer["Application Layer"]
        FlaskApp["Flask Application<br/>app.py"]
        
        ConfigEndpoint["GET /config<br/>Returns scorecard info"]
        CalcEndpoint["POST /calculate<br/>Scores applicants"]
        
        HTMLTemplate["templates/index.html<br/>User Interface"]
        JSScript["static/js/app.js<br/>Client Logic"]
        CSSStyle["static/css/style.css<br/>Styling"]
        
        ScorecardLoader["Load final_scorecard.csv<br/>In-Memory"]
        ScoreCalculator["Calculate Score<br/>WOE Lookup + Sum"]
    end
    
    subgraph Utilities["Utility Modules"]
        ConfigMgr["Configuration Manager"]
        Logger["Logging Module"]
        FileHandler["File I/O Handler"]
    end
    
    subgraph Storage["Data Storage"]
        ScorecardCSV["final_scorecard.csv"]
        ConfigJSON["config.json"]
        DataCSV["german_credit_data.csv"]
    end
    
    GermanURL --> LoadData
    AustralianURL --> LoadData
    JapaneseURL --> LoadData
    
    LoadData --> CleanData
    CleanData --> MergeDatasets
    MergeDatasets --> HandleMissing
    
    HandleMissing --> BinFeatures
    BinFeatures --> ComputeWOE
    ComputeWOE --> ComputeIV
    ComputeIV --> EncodeFeatures
    
    EncodeFeatures --> LogRegModel
    EncodeFeatures --> RFModel
    EncodeFeatures --> XGBModel
    EncodeFeatures --> LGBModel
    
    LogRegModel --> CalcMetrics
    RFModel --> CalcMetrics
    XGBModel --> CalcMetrics
    LGBModel --> CalcMetrics
    
    CalcMetrics --> CompareModels
    CompareModels --> SelectBest
    
    SelectBest --> GenScorecard
    GenScorecard --> ScaleScores
    ScaleScores --> SaveScorecard
    
    SaveScorecard --> ScorecardCSV
    SaveScorecard --> ConfigJSON
    
    CalcMetrics --> PlotROC
    CalcMetrics --> PlotDist
    ComputeIV --> PlotFeatures
    CompareModels --> PlotComparison
    ComputeWOE --> PlotWOE
    
    ScorecardCSV --> ScorecardLoader
    ConfigJSON --> ScorecardLoader
    
    ScorecardLoader --> ScoreCalculator
    HTMLTemplate --> FlaskApp
    JSScript --> FlaskApp
    CSSStyle --> FlaskApp
    
    ConfigEndpoint --> ScorecardLoader
    CalcEndpoint --> ScoreCalculator
    
    FlaskApp -.->|Uses| ConfigMgr
    FlaskApp -.->|Uses| Logger
    SaveScorecard -.->|Uses| FileHandler"""
}

def create_mermaid_files():
    """Create .mmd files from diagram definitions"""
    print("Creating Mermaid diagram files...")
    for filename, content in DIAGRAMS.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created {filename}")

def convert_to_png():
    """Convert .mmd files to PNG using mermaid-cli"""
    print("\nConverting diagrams to PNG...")
    print("Installing mermaid-cli if not present...")
    
    # Try to install mermaid-cli
    try:
        subprocess.run(['npm', 'install', '-g', '@mermaid-js/mermaid-cli'], 
                      capture_output=True, timeout=60)
    except Exception as e:
        print(f"⚠️  Could not install mermaid-cli: {e}")
        print("Please install manually: npm install -g @mermaid-js/mermaid-cli")
        return False
    
    # Convert each diagram
    for filename in DIAGRAMS.keys():
        output_name = filename.replace('.mmd', '.png')
        try:
            print(f"Converting {filename} to {output_name}...")
            subprocess.run(['mmdc', '-i', filename, '-o', output_name], 
                          check=True, timeout=30)
            print(f"✓ Successfully created {output_name}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to convert {filename}: {e}")
        except FileNotFoundError:
            print(f"✗ mermaid-cli not found. Install with: npm install -g @mermaid-js/mermaid-cli")
            return False
    
    return True

def main():
    """Main execution"""
    print("=" * 60)
    print("German Credit Scorecard - Architecture Diagrams Exporter")
    print("=" * 60)
    
    # Create .mmd files
    create_mermaid_files()
    
    # Try to convert to PNG
    success = convert_to_png()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All diagrams exported successfully!")
        print("\nGenerated PNG files:")
        for filename in DIAGRAMS.keys():
            png_file = filename.replace('.mmd', '.png')
            print(f"  - {png_file}")
    else:
        print("⚠️  PNG conversion requires Node.js and mermaid-cli")
        print("\nAlternative options:")
        print("1. Install Node.js: https://nodejs.org/")
        print("2. Then run: npm install -g @mermaid-js/mermaid-cli")
        print("3. Then run this script again")
        print("\nOR use Mermaid Live Editor:")
        print("   → Go to https://mermaid.live")
        print("   → Paste diagram code")
        print("   → Download as PNG")
        print("\n.mmd files have been created for manual conversion")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
