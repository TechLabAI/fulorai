import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyFeatureStageEditorComponent } from './jrny-feature-stage-editor.component';

describe('JrnyFeatureStageEditorComponent', () => {
  let component: JrnyFeatureStageEditorComponent;
  let fixture: ComponentFixture<JrnyFeatureStageEditorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyFeatureStageEditorComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyFeatureStageEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
